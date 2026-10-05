# ------------------------------------------------------------
"""
Author: Hanan Abdulwahab Siala
Supervisor: Kevin Lano
University: King's College London
Date: 27-09-2026
"""
# ------------------------------------------------------------
import argparse
import os
import re
import sys

from model_service import (
   load_model,
   unload_model,
   generate_inference_output,
   post_process_uml,
   post_process_ocl,
   create_metrics_text,
   is_model_loaded,
   get_loaded_model_info,
)

from graphviz_service import generate_graphviz_diagram
# ------------------------------------------------------------
DEFAULT_LANGUAGE = "Java"
DEFAULT_TASK = "UML"
DEFAULT_UML_MODEL_VERSION = 4
DEFAULT_OCL_MODEL_VERSION = 2
DEFAULT_MODEL_TYPE = "LoRA Adapter"
DEFAULT_UML_DETAIL = "Detailed Class Diagram"
DEFAULT_UML_PARAMETERS = "Methods Only"
DEFAULT_UML_FORMAT = "PNG"
OUTPUT_DIRECTORY = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIRECTORY, "output.txt")
PREPROCESSED_JAVA = "Test1.java"
PREPROCESSED_PYTHON = "Test1.py"
# ------------------------------------------------------------
def CleanJavaCode(JavaCode):
   JavaCode = re.sub(r'//.*', '', JavaCode)
   JavaCode = re.sub(r'/\*[\s\S]*?\*/', '', JavaCode)
   JavaCode = re.sub(r'^\s*package\s+[^\s;]+;\s*', '', JavaCode, flags=re.MULTILINE)
   JavaCode = re.sub(r'^\s*import\s+[^\s;]+;\s*', '', JavaCode, flags=re.MULTILINE)
   JavaCode = re.sub(r'""".*?"""', '""', JavaCode, flags=re.DOTALL)
   JavaCode = '\n'.join(line for line in JavaCode.splitlines() if line.strip())
   return JavaCode
# ------------------------------------------------------------
def CleanPythonCode(PythonCode):
   PythonCode = re.sub(r'#.*', '', PythonCode)
   PythonCode = re.sub(r'(\'\'\'[\s\S]*?\'\'\'|\"\"\"[\s\S]*?\"\"\")', '', PythonCode)
   PythonCode = re.sub(r'^\s*from\s+[^\s;]+;\s*', '', PythonCode, flags=re.MULTILINE)
   PythonCode = re.sub(r'^\s*import\s+[^\s;]+;\s*', '', PythonCode, flags=re.MULTILINE)
   CleanedLines = []
   Lines = PythonCode.split('\n')
   for line in Lines:
      if line.endswith('='):
         line += '"String"'
         CleanedLines.append(line)
      if not line.strip():
         continue
      LeadingSpaces = (len(line) - len(line.lstrip()))
      CleanedLines.append(' ' * LeadingSpaces + line.strip())
   CleanedFile = '\n'.join(CleanedLines)
   return CleanedFile
# ------------------------------------------------------------
def CheckFileEmpty(File):
   if os.path.getsize(File) == 0:
      return ""
   else:
      with open(File, 'r', encoding="utf-8") as file:
         Content = file.read()
      return Content
# ------------------------------------------------------------
def CleaningFile(SourceFile, DestinationFile, Language):
   try:
      with open(SourceFile, 'r', encoding="utf-8") as file:
         Program = file.read()
      if Language == "Java":
         InputFile = CleanJavaCode(Program)
      else:
         InputFile = CleanPythonCode(Program)
      if os.path.exists(DestinationFile):
         os.remove(DestinationFile)
      with open(DestinationFile, "w", encoding="utf-8") as file:
         file.write(InputFile)
      return True
   except FileNotFoundError:
      print(f"File not found: {SourceFile}")
      return False
# ------------------------------------------------------------
def PutTogether(InputProgram, SourceFile, Language):
   CodeList = []
# ------------------------------------------------------------
   if os.path.isfile(InputProgram):
      if (Language == "Java" and InputProgram.endswith(".java")) or (Language == "Python" and InputProgram.endswith(".py")):
         with open(InputProgram, "r", encoding="utf-8") as f:
            Code = f.read()
            CodeList.append(Code)
      else:
         raise ValueError(f"Input file is not a valid {Language} source file: {InputProgram}")
# ------------------------------------------------------------
   elif os.path.isdir(InputProgram):
      for root, dirs, files in os.walk(InputProgram):
         for file in files:
            if (Language == "Java" and file.endswith(".java")) or (Language == "Python" and file.endswith(".py")):
               FilePath = os.path.join(root, file)
               with open(FilePath, "r", encoding="utf-8") as f:
                  Code = f.read()
                  CodeList.append(Code)
   else:
      raise FileNotFoundError(f"Input path does not exist: {InputProgram}")
# ------------------------------------------------------------
   CombinedCode = "\n".join(CodeList)
   if os.path.exists(SourceFile):
      os.remove(SourceFile)
   with open(SourceFile, "w", encoding="utf-8") as file:
      file.write(CombinedCode)
# ------------------------------------------------------------
def LanguageIsJava(language):
   return language == "Java"
# ------------------------------------------------------------
def preprocess_directory(input_path, output_directory, language):
   os.makedirs(output_directory, exist_ok=True)
   if LanguageIsJava(language):
      FileName = "Temp.java"
      OutputFile = "Test1.java"
   else:
      FileName = "Temp.py"
      OutputFile = "Test1.py"
# ------------------------------------------------------------
   SourceFile = os.path.join(output_directory, FileName)
   DestinationFile = os.path.join(output_directory, OutputFile)
   if os.path.exists(SourceFile):
      os.remove(SourceFile)
   if os.path.exists(DestinationFile):
      os.remove(DestinationFile)
# ------------------------------------------------------------
   PutTogether(input_path, SourceFile, language)
# ------------------------------------------------------------
   success = CleaningFile(SourceFile, DestinationFile, language)
   if not success:
      raise RuntimeError("CleaningFile() failed.")
# ------------------------------------------------------------
   if os.path.exists(SourceFile):
      os.remove(SourceFile)
   return DestinationFile
# ------------------------------------------------------------
def parse_arguments():
   parser = argparse.ArgumentParser(
      description=("LLM4Models UML/OCL extractor.")
   )
   parser.add_argument(
      "input",
      help=("Java/Python source file or directory containing source files."),
   )
   parser.add_argument(
      "--language",
      choices=["Java", "Python"],
      default=DEFAULT_LANGUAGE,
   )
   parser.add_argument(
      "--task",
      choices=["UML", "OCL"],
      default=DEFAULT_TASK,
   )
   parser.add_argument(
      "--model-version",
      type=int,
      choices=[1, 2, 3, 4],
      default=None,
      help=(
         "Model version. "
         "Default is 4 for UML and 2 for OCL."
      ),
   )
   parser.add_argument(
      "--model-type",
      choices=["LoRA Adapter", "Full Model"],
      default=DEFAULT_MODEL_TYPE,
   )
   parser.add_argument(
      "--output-file",
      "--output",
      dest="output_file",
      default=OUTPUT_FILE,
      help=f"Output JSON text file. Default: {OUTPUT_FILE}",
   )
# ------------------------------------------------------------
   parser.add_argument(
      "--uml-detail",
      choices=["Detailed Class Diagram", "Outline Class Diagram"],
      default=DEFAULT_UML_DETAIL,
      help= "UML diagram type. Default: Detailed Class Diagram",
   )
   parser.add_argument(
      "--uml-parameters",
      choices=["Methods with Parameter Names and Types", "Methods with Parameter Types", "Methods Only"],
      default=DEFAULT_UML_PARAMETERS,
      help="How method parameters are displayed. Default: Methods Only",
   )
   parser.add_argument(
      "--uml-format",
      choices=["PNG", "PDF", "SVG"],
      default=DEFAULT_UML_FORMAT,
      help= "Graphviz output format. Default: PNG",
   )
   return parser.parse_args()
# ------------------------------------------------------------
def validate_configuration(language, task, version):
   if task == "UML":
      if version not in [1, 2, 3, 4]:
         raise ValueError("UML version must be 1, 2, 3, or 4.")
   elif task == "OCL":
      if version not in [1, 2]:
         raise ValueError("OCL version must be 1 or 2.")
   else:
      raise ValueError("Task must be UML or OCL.")
# ------------------------------------------------------------
def run_graphviz(output_directory, uml_detail, uml_parameters, uml_format):
   print()
   print("Starting Graphviz generation...", flush=True)
   print(f"Diagram type : {uml_detail}")
   print(f"Parameters   : {uml_parameters}")
   print(f"Format       : {uml_format}")
   try:
      graphviz_result = generate_graphviz_diagram(output_directory, uml_detail, uml_parameters, uml_format)
   except Exception as exc:
      print("ERROR: Graphviz generation failed.")
      print(f"Reason: {type(exc).__name__}: {exc}")
      return False
   if not graphviz_result["success"]:
      print("ERROR: Graphviz generation failed.")
      print(f"Reason: {graphviz_result['error']}")
      return False
   print()
   print("Graphviz generation completed.")
   print(f"DOT file : {graphviz_result['dot_file']}")
   print(f"Diagram  : {graphviz_result['output_file']}")
   print(f"Format   : {graphviz_result['format']}")
   return True
# ------------------------------------------------------------
def main():
   args = parse_arguments()
   language = args.language
   task = args.task
   if args.model_version is None:
      if task == "UML":
         model_version = DEFAULT_UML_MODEL_VERSION
      else:
         model_version = DEFAULT_OCL_MODEL_VERSION
   else:
      model_version = args.model_version

   if task == "UML" and model_version not in [1, 2, 3, 4]:
      raise ValueError("UML model version must be 1, 2, 3, or 4.")
   if task == "OCL" and model_version not in [1, 2]:
      raise ValueError("OCL model version must be 1 or 2.")

   if task=="UML" and args.model_type not in ["LoRA Adapter", "Full Model"]:
      args.model_type = "LoRA Adapter"
   model_type = args.model_type
   input_path = args.input
# ------------------------------------------------------------
   if not os.path.exists(input_path):
      print(f"ERROR: Input path does not exist: " f"{input_path}")
      raise SystemExit(1)
# ------------------------------------------------------------
   if not os.path.isfile(input_path) and not os.path.isdir(input_path):
      print(f"ERROR: Input must be a source file or directory: {input_path}")
      raise SystemExit(1)
# ------------------------------------------------------------
   if os.path.isfile(input_path):
      if language == "Java":
         if not input_path.lower().endswith(".java"):
            print("ERROR: Java input file must have a .java extension.")
            raise SystemExit(1)
      elif language == "Python":
         if not input_path.lower().endswith(".py"):
            print("ERROR: Python input file must have a .py extension.")
            raise SystemExit(1)
# ------------------------------------------------------------
   try:
      validate_configuration(language=language, task=task, version=model_version)
   except ValueError as exc:
      print(f"ERROR: {exc}")
      raise SystemExit(1)
   output_file = args.output_file
# ------------------------------------------------------------
   print("=" * 70)
   print("LLM4Models UML/OCL EXTRACTOR")
   print("=" * 70)
   print(f"Input       : {input_path}")
   print(f"Language    : {language}")
   print(f"Task        : {task}")
   print(f"Version     : {model_version}")
   print(f"Model type  : {model_type}")
   print(f"Output      : {output_file}")
   if task == "UML":
      if args.uml_detail == "Detailed Class Diagram":
         if args.uml_parameters not in ["Methods with Parameter Names and Types", "Methods with Parameter Types", "Methods Only"]:
            args.uml_parameters = "Methods Only"
      elif args.uml_detail == "Outline Class Diagram":
         args.uml_parameters = ""
      else:
         args.uml_detail = "Detailed Class Diagram"
         args.uml_parameters = "Methods Only"
      if args.uml_format not in ["PNG", "PDF", "SVG"]:
         args.uml_format = "PNG"
      print(f"UML detail  : {args.uml_detail}")
      print(f"Parameters  : {args.uml_parameters}")
      print(f"Format      : {args.uml_format}")
   print("=" * 70)
# ------------------------------------------------------------
   print()
   print("Starting preprocessing...", flush=True)
   try:
      input_file = preprocess_directory(input_path=input_path, output_directory=OUTPUT_DIRECTORY, language=language)
   except Exception as exc:
      print("ERROR: Preprocessing failed.")
      print(f"Reason: {type(exc).__name__}: {exc}")
      raise SystemExit(1)
   print(f"Preprocessed file: {input_file}")
# ------------------------------------------------------------
   if not os.path.isfile(input_file):
      print(f"ERROR: File does not exist: " f"{input_file}")
      raise SystemExit(1)
   if os.path.getsize(input_file) == 0:
      print("ERROR: Input file is empty.")
      raise SystemExit(1)
# ------------------------------------------------------------
   try:
      with open(input_file, "r", encoding="utf-8") as file:
         code = file.read()
   except Exception as exc:
      print("ERROR: Could not read input file.")
      print(f"Reason: {exc}")
      raise SystemExit(1)
   print(f"Input characters: {len(code)}", flush=True)
# ------------------------------------------------------------
   print("Loading model...", flush=True)
   try:
      load_model(language=language, task=task, version=model_version, model_type=model_type)
   except Exception as exc:
      print("ERROR: Model loading failed.")
      print(f"Reason: {exc}")
      raise SystemExit(1)
   if not is_model_loaded():
      print("ERROR: Model was not loaded.")
      raise SystemExit(1)
   info = get_loaded_model_info()
   print("Model loaded successfully.", flush=True)
   print(f"Checkpoint: {info['checkpoint']}")
# ------------------------------------------------------------
   print()
   print("Starting inference...", flush=True)
   print("Maximum new tokens: 32768", flush=True)
   try:
      (
         output,
         input_tokens,
         generated_tokens,
         inference_time,
      ) = generate_inference_output(
         code,
         return_metrics=True,
      )
   except Exception as exc:
      print("ERROR: Inference failed.")
      print(f"Reason: {exc}")
      unload_model()
      raise SystemExit(1)
   if output is None or not str(output).strip():
      print("ERROR: Model returned empty output.")
      unload_model()
      raise SystemExit(1)
# ------------------------------------------------------------
   output_directory = os.path.dirname(output_file)
   if output_directory:
      os.makedirs(output_directory, exist_ok=True)
   try:
      with open(output_file, "w", encoding="utf-8") as file:
         file.write(str(output))
   except Exception as exc:
      print("ERROR: Could not save output file.")
      print(f"Reason: {exc}")
      unload_model()
      raise SystemExit(1)
# ------------------------------------------------------------
   metrics = create_metrics_text(
      language=language,
      task=task,
      model_type=model_type,
      model_version=model_version,
      input_tokens=input_tokens,
      generated_tokens=generated_tokens,
      inference_time=inference_time,
   )
   metrics_file = os.path.join(output_directory if output_directory else ".", "inference_metrics.txt")
   with open(metrics_file, "w", encoding="utf-8") as file:
      file.write(metrics)
   print()
   print("JSON output saved to:")
   print(output_file)
   print()
   print("Inference metrics:")
   print(metrics)
   print()
   print(f"Metrics saved to: {metrics_file}")
# ------------------------------------------------------------
   print()
   print("Starting post-processing...", flush=True)
# ------------------------------------------------------------
   if task == "UML":
      result = post_process_uml(
         input_file=output_file,
         output_directory=(output_directory if output_directory else "."),
         language=language,
      )
      if not result["success"]:
         print("ERROR: UML post-processing failed.")
         print(f"Reason: {result['error']}")
         unload_model()
         raise SystemExit(1)
      print()
      print("UML post-processing completed.")
      print(f"UML classes saved to: " f"{result['uml_file']}")
      print(f"UML relationships saved to: " f"{result['rel_file']}")
# ------------------------------------------------------------
      graphviz_success = run_graphviz(
         output_directory=(output_directory if output_directory else "."),
         uml_detail=args.uml_detail,
         uml_parameters=args.uml_parameters,
         uml_format=args.uml_format,
      )
      if not graphviz_success:
         print()
         print("WARNING: UML post-processing succeeded, but Graphviz generation failed.")
# ------------------------------------------------------------
   else:
      result = post_process_ocl(
         input_file=output_file,
         output_directory=(output_directory if output_directory else "."),
      )
      if not result["success"]:
         print("ERROR: OCL post-processing failed.")
         print(f"Reason: {result['error']}")
         unload_model()
         raise SystemExit(1)
      print()
      print("OCL post-processing completed.")
      print(f"OCL saved to: " f"{result['ocl_file']}")
   print()
   print(f"Output saved to: {output_file}")
   print(f"Metrics saved to: {metrics_file}")
# ------------------------------------------------------------
   unload_model()
# ------------------------------------------------------------
if __name__ == "__main__":
   main()
# ------------------------------------------------------------
