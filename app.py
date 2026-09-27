# ------------------------------------------------------------
"""
Author: Hanan Abdulwahab Siala
Supervisor: Kevin Lano
University: King's College London
Date: 27-09-2026
"""
# ------------------------------------------------------------
import os
import re

import gradio as gr

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
MODEL_FAMILY = "Mistral"
LANGUAGES = ["Java", "Python"]
TASKS = ["UML", "OCL"]
MODEL_TYPES = ["LoRA Adapter", "Full Model"]
OUTPUT_DIRECTORY = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIRECTORY, "output.txt")
# ------------------------------------------------------------
def enable_program_inputs():
   return (
      gr.update(interactive=True),   # Program Directory
      gr.update(interactive=True),   # Load Program Directory
      gr.update(interactive=True),   # Load Program File
      gr.update(interactive=True),   # Java / Python Program
   )
# ------------------------------------------------------------
def disable_program_inputs():
   return (
      gr.update(interactive=False),  # Program Directory
      gr.update(interactive=False),  # Load Program Directory
      gr.update(interactive=False),  # Load Program File
      gr.update(interactive=False),  # Java / Python Program
   )
# ------------------------------------------------------------
def update_output_files(task_value):
   if task_value == "UML":
      return """
### Current output files

- `output/output.txt` — raw JSON response from the LLM
- `output/inference_metrics.txt` — inference metrics
- `output/Test1.UML` — extracted UML classes
- `output/Test1.REL` — extracted UML relationships
- `output/Test1.dot` — Graphviz DOT source
- `output/Test1.png` / `.pdf` / `.svg` — generated UML diagram
"""
   if task_value == "OCL":
      return """
### Current output files

- `output/output.txt` — raw JSON response from the LLM
- `output/inference_metrics.txt` — inference metrics
- `output/Test1.OCL` — generated OCL specification
"""

   return """
### Current output files

No task selected.
"""
# ------------------------------------------------------------
def clear_program_directory():
   return gr.update(value="")
# ------------------------------------------------------------
def load_program_directory(input_directory, language):
   if not input_directory:
      return ""
   if not os.path.isdir(input_directory):
      return ""
   try:
      code_list = []
      extension = (".java" if language == "Java" else ".py")
      for root, dirs, files in os.walk(input_directory):
         for file in files:
            if not file.endswith(extension):
               continue
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
               code_list.append(f.read())
      if not code_list:
         return ""
      combined_code = "\n".join(code_list)
      return combined_code
   except Exception:
      return ""
# ------------------------------------------------------------
def set_uml_postprocessed_state():
   return (
      gr.update(interactive=False),  # Pre-process
      gr.update(interactive=False),  # Analyze
      gr.update(interactive=True),   # Post-process UML
      gr.update(interactive=False),  # Post-process OCL
   )
# ------------------------------------------------------------
def clear_generated_results():
   return (
      "",
      "",
      None,
      None,
      "",
      None,
   )
# ------------------------------------------------------------
def update_task_outputs(task_value):
   if task_value == "UML":
      return (
         gr.update(visible=True),
         gr.update(visible=True),
         gr.update(visible=False),
         gr.update(visible=False),
      )
   if task_value == "OCL":
      return (
         gr.update(visible=False),
         gr.update(visible=False),
         gr.update(visible=True),
         gr.update(visible=True),
      )
   return (
      gr.update(visible=False),
      gr.update(visible=False),
      gr.update(visible=False),
      gr.update(visible=False),
    )
# ------------------------------------------------------------
def update_uml_postprocess_button(task_value, detail_value, parameters_value, format_value):
   if task_value != "UML":
      return gr.update(interactive=False)
   if not detail_value:
      return gr.update(interactive=False)
   if not format_value:
      return gr.update(interactive=False)
   if (detail_value == "Detailed Class Diagram" and not parameters_value):
      return gr.update(interactive=False)
   return gr.update(interactive=True)
# ------------------------------------------------------------
def update_uml_controls(task_value):
   if task_value == "UML":
      return (
         gr.update(
            visible=True,
            interactive=True,
            value=None,
         ),
         gr.update(
            visible=False,
            interactive=False,
            value=None,
         ),
         gr.update(
            visible=True,
            interactive=True,
            value=None,
         ),
      )
   return (
      gr.update(
         visible=False,
         interactive=False,
         value=None,
      ),
      gr.update(
         visible=False,
         interactive=False,
         value=None,
      ),
      gr.update(
         visible=False,
         interactive=False,
         value=None,
      ),
   )
# ------------------------------------------------------------
def update_uml_parameters(detail_value):
   if detail_value == "Detailed Class Diagram":
      return gr.update(
         visible=True,
         interactive=True,
      )
   return gr.update(
      visible=False,
      interactive=False,
      value=None,
   )
# ------------------------------------------------------------
def hide_uml_controls():
   return (
      gr.update(
         visible=False,
         interactive=False,
         value=None,
      ),
      gr.update(
         visible=False,
         interactive=False,
         value=None,
      ),
      gr.update(
         visible=False,
         interactive=False,
         value=None,
      ),
   )
# ------------------------------------------------------------
def uml_selection_changed(task_value, detail_value, parameters_value, format_value):
   if task_value != "UML":
      return gr.update(interactive=False)
   if not detail_value:
      return gr.update(interactive=False)
   if detail_value == "Detailed Class Diagram":
      if not parameters_value:
         return gr.update(interactive=False)
   if not format_value:
      return gr.update(interactive=False)
   return gr.update(interactive=True)
# ------------------------------------------------------------
def update_postprocess_buttons(task_value):
   if task_value == "UML":
      return (
         gr.update(interactive=True),
         gr.update(interactive=False),
      )
   if task_value == "OCL":
      return (
         gr.update(interactive=False),
         gr.update(interactive=True),
      )
   return (
      gr.update(interactive=False),
      gr.update(interactive=False),
   )
# ------------------------------------------------------------
def set_pipeline_state(state, task_value):
   if state == "clear":
      return (
         gr.update(interactive=False),  # preprocess
         gr.update(interactive=False),  # analyze
         gr.update(interactive=False),  # UML
         gr.update(interactive=False),  # OCL
      )
   if state == "program":
      return (
         gr.update(interactive=True),
         gr.update(interactive=False),
         gr.update(interactive=False),
         gr.update(interactive=False),
      )
   if state == "preprocessed":
      return (
         gr.update(interactive=False),
         gr.update(interactive=True),
         gr.update(interactive=False),
         gr.update(interactive=False),
      )
   if state == "analyzed":
      if task_value == "UML":
         return (
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=True),
            gr.update(interactive=False),
         )
      if task_value == "OCL":
         return (
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=True),
         )
   if state == "postprocessed":
      return (
         gr.update(interactive=False),
         gr.update(interactive=False),
         gr.update(interactive=False),
         gr.update(interactive=False),
      )
   return (
      gr.update(interactive=False),
      gr.update(interactive=False),
      gr.update(interactive=False),
      gr.update(interactive=False),
   )
# ------------------------------------------------------------
def program_input_changed(program_text):
   if program_text and program_text.strip():
      return set_pipeline_state("program", None)
   else:
      return set_pipeline_state("clear", None)
# ------------------------------------------------------------
def _loaded_model_text(info):
   if not info:
      return "No model loaded."
   return (
      f"Model: {info['model_family']}\n"
      f"Language: {info['language']}\n"
      f"Task: {info['task']}\n"
      f"Version: {info['version']}\n"
      f"Model Type: {info['model_type']}\n"
      f"Checkpoint: {info['checkpoint']}"
   )
# ------------------------------------------------------------
def _version_choices(language, task):
   if task == "UML":
      return gr.update(
         choices=["1", "2", "3", "4"],
         value="4",
         interactive=True,
      )
   return gr.update(
      choices=["1", "2"],
      value="2",
      interactive=True,
   )
# ------------------------------------------------------------
def configuration_changed(language, task, model_version, model_type):
   unload_model()
   version_update = _version_choices(language, task)
   return (
      version_update,
      "",
      None,
      "",
      "No model loaded.",
   )
# ------------------------------------------------------------
def language_changed(language, task, model_version, model_type):
   return configuration_changed(
      language,
      task,
      model_version,
      model_type,
   )
# ------------------------------------------------------------
def task_changed(language, task, model_version, model_type):
   unload_model()
   version_update = _version_choices(
      language,
      task,
   )
   return (
      version_update,
      "",
      None,
      "",
      "No model loaded.",
   )
# ------------------------------------------------------------
def version_changed(language, task, model_version, model_type):
   unload_model()
   return (
      "",
      None,
      "",
      "No model loaded.",
   )
# ------------------------------------------------------------
def model_type_changed(language, task, model_version, model_type):
   unload_model()
   return (
      "",
      None,
      "",
      "No model loaded.",
   )
# ------------------------------------------------------------
def load_selected_model(language, task, model_version, model_type):
   try:
      version = int(model_version)
      info = load_model(
         language=language,
         task=task,
         version=version,
         model_type=model_type,
      )
      status = (
         "Model loaded successfully.\n\n"
         + _loaded_model_text(info)
      )
      return (
         status,
         "",
         None,
         "",
         "",
         "",
         None,
         None,
         "",
         None,
      )
   except Exception as exc:
      return (
         "ERROR: Could not load model.\n\n"
         f"{type(exc).__name__}: {exc}",
         "",
         None,
         "",
         "",
         "",
         None,
         None,
         "",
         None,
      )
# ------------------------------------------------------------
def CleanJavaCode(JavaCode):
   JavaCode = __import__("re").sub(r'//.*', '', JavaCode)
   JavaCode = __import__("re").sub(r'/\*[\s\S]*?\*/', '', JavaCode)
   JavaCode = __import__("re").sub(r'^\s*package\s+[^\s;]+;\s*', '', JavaCode, flags=__import__("re").MULTILINE)
   JavaCode = __import__("re").sub(r'^\s*import\s+[^\s;]+;\s*', '', JavaCode, flags=__import__("re").MULTILINE)
   JavaCode = __import__("re").sub(r'""".*?"""', '""', JavaCode, flags=__import__("re").DOTALL)
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
def CleaningFile(SourceFile, DestinationFile, Language):
   try:
      with open(SourceFile, "r", encoding="utf-8") as file:
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
      return False
# ------------------------------------------------------------
def PutTogether(InputDirectoryProgram, SourceFile, Language):
   JavaCodeList = []
   for root, dirs, files in os.walk(InputDirectoryProgram):
      for file in files:
         if (Language == "Java" and file.endswith(".java")) or (Language == "Python" and file.endswith(".py")):
            FilePath = os.path.join(root, file)
            with open(FilePath, "r", encoding="utf-8") as f:
               JavaCode = f.read()
               JavaCodeList.append(JavaCode)
   CombinedCode = "\n".join(JavaCodeList)
   if os.path.exists(SourceFile):
      os.remove(SourceFile)
   with open(SourceFile, "w", encoding="utf-8") as file:
      file.write(CombinedCode)
# ------------------------------------------------------------
def load_program_file(file_path):
   if not file_path:
      return ""
   try:
      with open(file_path, "r", encoding="utf-8") as file:
         return file.read()
   except Exception:
      return ""
# ------------------------------------------------------------
def preprocess_program(code, language):
   if not code or not code.strip():
      return (
         "ERROR: Please load or enter "
         "a program first.",
         code,
      )
   try:
      if language == "Java":
         cleaned = CleanJavaCode(code)
      else:
         cleaned = CleanPythonCode(code)
      return (
         "Pre-processing completed successfully.",
         cleaned,
      )
   except Exception as exc:
      return (
         "ERROR during preprocessing.\n\n"
         f"{type(exc).__name__}: {exc}",
         code,
      )
# ------------------------------------------------------------
def analyze_code(code, language, task):
   if not is_model_loaded():
      return ("ERROR: No model is loaded.\n" "Please select the model configuration and press Load Model first.", "")
   if not code or not code.strip():
      return ("Please enter or load code first.", "")
   try:
      info = get_loaded_model_info()
      if info["language"] != language:
         return ("ERROR: The selected language does not match the loaded model.\n\n" f"Loaded language: {info['language']}\n" f"Selected language: {language}\n\n" "Please press Load Model.", "")
      if info["task"] != task:
         return ("ERROR: The selected task does not match the loaded model.\n\n" f"Loaded task: {info['task']}\n" f"Selected task: {task}\n\n" "Please press Load Model.", "")
      (
          raw_output,
          input_tokens,
          generated_tokens,
          inference_time,
      ) = generate_inference_output(code, return_metrics=True)
      if (raw_output is None or not str(raw_output).strip()):
         return ("ERROR: Model returned empty output.", "")
# ------------------------------------------------------------
      os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
      with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
         file.write(str(raw_output))
# ------------------------------------------------------------
      metrics = create_metrics_text(
         language=language,
         task=task,
         model_type=info["model_type"],
         model_version=info["version"],
         input_tokens=input_tokens,
         generated_tokens=generated_tokens,
         inference_time=inference_time,
      )
      metrics_file = os.path.join(OUTPUT_DIRECTORY, "inference_metrics.txt")
      with open(metrics_file, "w", encoding="utf-8") as file:
         file.write(metrics)
# ------------------------------------------------------------
      return (str(raw_output), metrics)
   except Exception as exc:
      return ("ERROR during analysis.\n\n" f"{type(exc).__name__}: {exc}", "")
# ------------------------------------------------------------
def postprocess_uml(language, uml_detail, uml_parameters, uml_format):
   if not uml_detail:
      uml_detail = "Detailed Class Diagram"
   if not uml_parameters:
      uml_parameters = "Methods Only"
   if not uml_format:
      uml_format = "PNG"
   if not os.path.isfile(OUTPUT_FILE):
      return ("ERROR: output/output.txt does not exist.", None, None)
   try:
      result = post_process_uml(
         input_file=OUTPUT_FILE,
         output_directory=OUTPUT_DIRECTORY,
         language=language,
      )
      if not result["success"]:
         return ("ERROR during UML post-processing.\n\n" f"{result['error']}", None, None)
      graphviz_result = generate_graphviz_diagram(
         OUTPUT_DIRECTORY,
         uml_detail,
         uml_parameters,
         uml_format,
      )
      if not graphviz_result["success"]:
         return ("UML extraction completed, but Graphviz failed.\n\n" f"{graphviz_result['error']}", None, None)
      output_file = graphviz_result["output_file"]
      if not output_file or not os.path.isfile(output_file):
         return ("UML post-processing completed, but the generated diagram file was not found.\n\n" f"Expected file:\n{output_file}", None, None)
      if uml_format == "PNG":
         image_file = output_file
      else:
         image_file = None
      status = (
         "UML post-processing completed successfully.\n\n"
         f"Classes: {result['uml_file']}\n"
         f"Relationships: {result['rel_file']}\n\n"
         f"Graphviz DOT: {graphviz_result['dot_file']}\n"
         f"Diagram: {output_file}\n"
         f"Format: {uml_format}"
      )
      return (status, image_file, output_file)
   except Exception as exc:
      return ("ERROR during UML post-processing.\n\n" f"{type(exc).__name__}: {exc}", None, None)
# ------------------------------------------------------------
def postprocess_ocl():
   if not os.path.isfile(OUTPUT_FILE):
      return ("ERROR: output/output.txt does not exist.", "", None)
   try:
      result = post_process_ocl(
         input_file=OUTPUT_FILE,
         output_directory=OUTPUT_DIRECTORY,
      )
      if not result["success"]:
         return ("ERROR during OCL post-processing.\n\n" f"{result['error']}", "", None)
      ocl_file = result["ocl_file"]
# ------------------------------------------------------------
      ocl_text = ""
      if ocl_file and os.path.isfile(ocl_file):
         with open(ocl_file, "r", encoding="utf-8") as file:
            ocl_text = file.read()
      status = "OCL post-processing completed successfully.\n\n" f"OCL file: {ocl_file}"
      return (status, ocl_text, ocl_file)
   except Exception as exc:
      return ("ERROR during OCL post-processing.\n\n" f"{type(exc).__name__}: {exc}", "", None)
# ------------------------------------------------------------
def clear_program():
   return (
      "",       # program
      None,     # program_file
      "",       # result
      "",       # inference_metrics
      "",       # preprocess_status
      "",       # postprocess_status
      None,     # uml_image
      None,     # uml_output_file
      "",       # ocl_result
      None,     # ocl_output_file
   )
# ------------------------------------------------------------
with gr.Blocks(title="LLM4Models UML/OCL Extractor") as app:
   gr.Markdown("# LLM4Models UML/OCL Extractor")
   gr.Markdown("Infer UML class diagrams and OCL specifications from Java and Python programs.")
   gr.Markdown(
      """
      ## Before You Start

      This system is designed primarily for object-oriented Java and Python programs.
      """
   )
   limitations_text = gr.Textbox(
   label="Supported Programs and Limitations",
   value="""• Supported languages: Java and Python.

• UML Class Diagram extraction is intended primarily for object-oriented programs containing classes, interfaces, attributes, methods, constructors, and relationships.

• Purely procedural programs or scripts without meaningful class/object-oriented structure are not appropriate for UML Class Diagram extraction.

• Programs consisting mainly of standalone functions, data-processing pipelines, configuration files, or other non-object-oriented structures may not produce meaningful UML class diagrams.

• Highly dynamic code, reflection, metaprogramming, runtime-generated classes, and runtime modifications may not be fully represented.

• Incomplete, syntactically invalid, truncated, or partially generated source code may produce incomplete results.

• External-library behavior that is not visible in the supplied source code may not be represented completely.

• The generated UML represents structure inferred from the supplied source code and does not guarantee the complete runtime architecture.

• For best results, provide complete and reasonably self-contained object-oriented Java or Python source code.""",
   lines=8,
   max_lines=8,
   interactive=False,
   show_copy_button=False,
   scale=1,
)
# ------------------------------------------------------------
   with gr.Row():
      language = gr.Dropdown(
         choices=LANGUAGES,
         value="Java",
         label="Language",
      )
      task = gr.Dropdown(
         choices=TASKS,
         value="UML",
         label="Task",
      )
   with gr.Row():
      model_version = gr.Dropdown(
         choices=["1", "2", "3", "4"],
         value="2",
         label="Model Version",
      )
      model_type = gr.Dropdown(
         choices=MODEL_TYPES,
         value="LoRA Adapter",
         label="Model Type",
      )
# ------------------------------------------------------------
   load_model_button = gr.Button(
      "Load Model",
      variant="primary",
   )
   model_status = gr.Textbox(
      label="Model Status",
      value="No model loaded.",
      lines=7,
      interactive=False,
   )
# ------------------------------------------------------------
   program_directory = gr.Textbox(
      label="Program Directory",
      placeholder="Enter directory containing Java/Python files",
      interactive=False,
   )
   load_directory_button = gr.Button(
      "Load Program Directory",
      interactive=False,
   )
   program_file = gr.File(
      label="Load Program File",
      file_types=[".java", ".py", ".txt"],
      type="filepath",
      interactive=False,
   )
   program = gr.Code(
      label="Java / Python Program",
      language= None, #"java",
      lines=20,
      interactive=False,
   )
# ------------------------------------------------------------
   gr.Markdown("## Stage 1 — Pre-processing")
   with gr.Row():
      preprocess_button = gr.Button(
         "Pre-process",
         interactive=False,
      )
      preprocess_status = gr.Textbox(
         label="Pre-processing Status",
         interactive=False,
      )
# ------------------------------------------------------------
   gr.Markdown("## Stage 2 — LLM4Models Inference")
   with gr.Row():
      analyze_button = gr.Button(
         "Analyze",
         variant="primary",
         interactive=False,
      )
      clear_button = gr.Button(
         "Clear",
      )
   result = gr.Textbox(
      label="JSON Result",
      lines=15,
      interactive=False,
   )
   inference_metrics = gr.Textbox(
      label="Inference Metrics",
      lines=8,
      interactive=False,
   )
# ------------------------------------------------------------
   gr.Markdown("## Stage 3 — Post-processing")
   uml_detail = gr.Dropdown(
      choices=[
         "Detailed Class Diagram",
         "Outline Class Diagram",
      ],
      value=None,
      label="UML Diagram Type",
      interactive=False,
      visible=False,
   )
   uml_parameters = gr.Dropdown(
      choices=[
         "Methods with Parameter Names and Types",
         "Methods with Parameter Types",
         "Methods Only",
      ],
      value=None,
      label="Method Parameters",
      interactive=False,
      visible=False,
   )
   uml_format = gr.Dropdown(
      choices=["PNG", "PDF", "SVG"],
      value=None,
      label="Output Format",
      interactive=False,
      visible=False,
   )
   with gr.Row():
      postprocess_uml_button = gr.Button(
         "Post-process UML",
         interactive=False,
      )
      postprocess_ocl_button = gr.Button(
         "Post-process OCL",
         interactive=False,
      )
   uml_image = gr.Image(
      label="Generated UML Diagram",
      type="filepath",
      visible=True,
   )
   uml_output_file = gr.File(
      label="Generated UML File",
      interactive=False,
      visible=True,
   )
   ocl_result = gr.Textbox(
      label="Generated OCL",
      lines=15,
      interactive=False,
      visible=False,
   )
   ocl_output_file = gr.File(
      label="Generated OCL File",
      visible=False,
   )
   postprocess_status = gr.Textbox(
      label="Post-processing Status",
      lines=6,
      interactive=False,
   )
   program.input(
      fn=program_input_changed,
      inputs=[program],
      outputs=[
         preprocess_button,
         analyze_button,
         postprocess_uml_button,
         postprocess_ocl_button,
      ],
   )
# ------------------------------------------------------------
   output_files_info = gr.Markdown(
      value=update_output_files("UML")
   )
# ------------------------------------------------------------
   load_model_button.click(
      fn=load_selected_model,
      inputs=[
         language,
         task,
         model_version,
         model_type,
      ],
      outputs=[
         model_status,
         program,
         program_file,
         result,
         inference_metrics,
         postprocess_status,
         uml_image,
         uml_output_file,
         ocl_result,
         ocl_output_file,
      ],
   ).then(
      fn=enable_program_inputs,
      inputs=[],
      outputs=[
         program_directory,
         load_directory_button,
         program_file,
         program,
      ],
   ).then(
      fn=update_task_outputs,
      inputs=[task],
      outputs=[
         uml_image,
         uml_output_file,
         ocl_result,
         ocl_output_file,
      ],
   )
   load_directory_button.click(
      fn=load_program_directory,
      inputs=[
         program_directory,
         language,
      ],
      outputs=[
         program,
      ],
   ).then(
      fn=program_input_changed,
      inputs=[program],
      outputs=[
         preprocess_button,
         analyze_button,
         postprocess_uml_button,
         postprocess_ocl_button,
      ],
   )
   program_file.change(
      fn=load_program_file,
      inputs=[program_file],
      outputs=[program],
   ).then(
      fn=lambda file: (set_pipeline_state("program", None) if file is not None else set_pipeline_state("clear", None)),
      inputs=[program_file],
      outputs=[
         preprocess_button,
         analyze_button,
         postprocess_uml_button,
         postprocess_ocl_button,
      ],
   )
   language.change(
      fn=language_changed,
      inputs=[
         language,
         task,
         model_version,
         model_type,
      ],
      outputs=[
         model_version,
         program,
         program_file,
         result,
         model_status,
      ],
   ).then(
      fn=disable_program_inputs,
      inputs=[],
      outputs=[
         program_directory,
         load_directory_button,
         program_file,
         program,
      ],
   ).then(          
      fn=hide_uml_controls,
      inputs=[],
      outputs=[
         uml_detail,
         uml_parameters,
         uml_format,
      ],
   ).then(          
      fn=lambda: set_pipeline_state(
         "clear",
         None,
      ),
      inputs=[],
      outputs=[
         preprocess_button,
         analyze_button,
         postprocess_uml_button,
         postprocess_ocl_button,
      ],
   )
   task.change(
      fn=task_changed,
      inputs=[
         language,
         task,
         model_version,
         model_type,
      ],
      outputs=[
         model_version,
         program,
         program_file,
         result,
         model_status,
      ],
   ).then(
      fn=clear_generated_results,
      inputs=[],
      outputs=[
         inference_metrics,
         postprocess_status,
         uml_image,
         uml_output_file,
         ocl_result,
         ocl_output_file,
      ],
   ).then(
      fn=disable_program_inputs,
      inputs=[],
      outputs=[
         program_directory,
         load_directory_button,
         program_file,
         program,
      ],
   )
   task.change(
      fn=update_task_outputs,
      inputs=[task],
      outputs=[
         uml_image,
         uml_output_file,
         ocl_result,
         ocl_output_file,
      ],
   ).then(
      fn=update_output_files,
      inputs=[task],
      outputs=[
         output_files_info,
      ],
   ).then(          
      fn=hide_uml_controls,
      inputs=[],
      outputs=[
         uml_detail,
         uml_parameters,
         uml_format,
      ],
   ).then(          
      fn=lambda: set_pipeline_state(
         "clear",
         None,
      ),
      inputs=[],
      outputs=[
         preprocess_button,
         analyze_button,
         postprocess_uml_button,
         postprocess_ocl_button,
      ],
   )
   uml_detail.change(
      fn=update_uml_parameters,
      inputs=[uml_detail],
      outputs=[uml_parameters],
   ).then(
      fn=update_uml_postprocess_button,
      inputs=[
         task,
         uml_detail,
         uml_parameters,
         uml_format,
      ],
      outputs=[postprocess_uml_button],
   )
   uml_parameters.change(
      fn=update_uml_postprocess_button,
      inputs=[
         task,
         uml_detail,
         uml_parameters,
         uml_format,
      ],
      outputs=[postprocess_uml_button],
   )
   uml_format.change(
      fn=update_uml_postprocess_button,
      inputs=[
         task,
         uml_detail,
         uml_parameters,
         uml_format,
      ],
      outputs=[postprocess_uml_button],
   )
   model_version.change(
      fn=version_changed,
      inputs=[
         language,
         task,
         model_version,
         model_type,
      ],
      outputs=[
         program,
         program_file,
         result,
         model_status,
      ],
   ).then(
      fn=disable_program_inputs,
      inputs=[],
      outputs=[
         program_directory,
         load_directory_button,
         program_file,
         program,
      ],
   ).then(          
      fn=hide_uml_controls,
      inputs=[],
      outputs=[
         uml_detail,
         uml_parameters,
         uml_format,
      ],
   ).then(          
      fn=lambda: set_pipeline_state(
         "clear",
         None,
      ),
      inputs=[],
      outputs=[
         preprocess_button,
         analyze_button,
         postprocess_uml_button,
         postprocess_ocl_button,
      ],
   )
   model_type.change(
      fn=model_type_changed,
      inputs=[
         language,
         task,
         model_version,
         model_type,
      ],
      outputs=[
         program,
         program_file,
         result,
         model_status,
      ],
   ).then(
      fn=disable_program_inputs,
      inputs=[],
      outputs=[
         program_directory,
         load_directory_button,
         program_file,
         program,
      ],
   ).then(          
      fn=hide_uml_controls,
      inputs=[],
      outputs=[
         uml_detail,
         uml_parameters,
         uml_format,
      ],
   ).then(          
      fn=lambda: set_pipeline_state(
         "clear",
         None,
      ),
      inputs=[],
      outputs=[
         preprocess_button,
         analyze_button,
         postprocess_uml_button,
         postprocess_ocl_button,
      ],
   )
   preprocess_button.click(
      fn=preprocess_program,
      inputs=[
         program,
         language,
      ],
      outputs=[
         preprocess_status,
         program,
      ],
   ).then(
      fn=lambda task_value: set_pipeline_state(
         "preprocessed",
         task_value,
      ),
      inputs=[task],
      outputs=[
         preprocess_button,
         analyze_button,
         postprocess_uml_button,
         postprocess_ocl_button,
      ],
   ).then(
      fn=disable_program_inputs,
      inputs=[],
      outputs=[
         program_directory,
         load_directory_button,
         program_file,
         program,
      ],
   )
   analyze_button.click(
      fn=analyze_code,
      inputs=[program, language, task],
      outputs=[result, inference_metrics,],
   ).then(
      fn=lambda task_value: set_pipeline_state(
         "analyzed",
         task_value,
      ),
      inputs=[task],
      outputs=[
         preprocess_button,
         analyze_button,
         postprocess_uml_button,
         postprocess_ocl_button,
      ],
   ).then(
      fn=update_uml_controls,
      inputs=[task],
      outputs=[
         uml_detail,
         uml_parameters,
         uml_format,
      ],
   )
   postprocess_uml_button.click(
      fn=postprocess_uml,
      inputs=[
         language,
         uml_detail,
         uml_parameters,
         uml_format,
      ],
      outputs=[
         postprocess_status,
         uml_image,
         uml_output_file,
      ],
   ).then(
      fn=set_uml_postprocessed_state,
      inputs=[],
      outputs=[
         preprocess_button,
         analyze_button,
         postprocess_uml_button,
         postprocess_ocl_button,
      ],
   )
   postprocess_ocl_button.click(
      fn=postprocess_ocl,
      inputs=[],
      outputs=[
         postprocess_status,
         ocl_result,
         ocl_output_file,
      ],
   ).then(
      fn=lambda: set_pipeline_state(
         "postprocessed",
         None,
      ),
      inputs=[],
      outputs=[
         preprocess_button,
         analyze_button,
         postprocess_uml_button,
         postprocess_ocl_button,
      ],
   )
   clear_button.click(
      fn=clear_program,
      inputs=[],
      outputs=[
         program,
         program_file,
         result,
         inference_metrics,
         preprocess_status,
         postprocess_status,
         uml_image,
         uml_output_file,
         ocl_result,
         ocl_output_file,
      ],
   ).then(
      fn=lambda: set_pipeline_state(
         "clear",
         None,
      ),
      inputs=[],
      outputs=[
         preprocess_button,
         analyze_button,
         postprocess_uml_button,
         postprocess_ocl_button,
      ],
   ).then(
      fn=enable_program_inputs,
      inputs=[],
      outputs=[
         program_directory,
         load_directory_button,
         program_file,
         program,
      ],
   ).then(
      fn=hide_uml_controls,
      inputs=[],
      outputs=[
         uml_detail,
         uml_parameters,
         uml_format,
      ],
   ).then(
      fn=clear_program_directory,
      inputs=[],
      outputs=[program_directory],
   )
# ------------------------------------------------------------
if __name__ == "__main__":
   port = int(os.environ.get("GRADIO_SERVER_PORT", "7860"))
   app.launch(server_name="0.0.0.0", server_port=port)
# ------------------------------------------------------------
