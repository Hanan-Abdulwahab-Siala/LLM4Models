import ast
import gc
import json
import os
import re
import threading
import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
# ------------------------------------------------------------
MISTRAL_BASE_MODEL = "mistralai/Mistral-7B-v0.3"
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
# ------------------------------------------------------------
MISTRAL_LORA_CHECKPOINTS = {
   # Java UML
   ("Java", "UML", 1, "LoRA Adapter"): "HA-Siala/Java-UML-v0.1",
   ("Java", "UML", 2, "LoRA Adapter"): "HA-Siala/Java-UML-v0.2",
   ("Java", "UML", 3, "LoRA Adapter"): "HA-Siala/Java-UML-v0.3",
   ("Java", "UML", 4, "LoRA Adapter"): "HA-Siala/Java-UML-v0.4",
   # Python UML
   ("Python", "UML", 1, "LoRA Adapter"): "HA-Siala/Python-UML-v0.1",
   ("Python", "UML", 2, "LoRA Adapter"): "HA-Siala/Python-UML-v0.2",
   ("Python", "UML", 3, "LoRA Adapter"): "HA-Siala/Python-UML-v0.3",
   ("Python", "UML", 4, "LoRA Adapter"): "HA-Siala/Python-UML-v0.4",
   # Java OCL
   ("Java", "OCL", 1, "LoRA Adapter"): "HA-Siala/Java-OCL-v0.1",
   ("Java", "OCL", 2, "LoRA Adapter"): "HA-Siala/Java-OCL-v0.2",
   # Python OCL
   ("Python", "OCL", 1, "LoRA Adapter"): "HA-Siala/Python-OCL-v0.1",
   ("Python", "OCL", 2, "LoRA Adapter"): "HA-Siala/Python-OCL-v0.2",
}
# ------------------------------------------------------------
MISTRAL_FULL_CHECKPOINTS = {
   # Java UML
   ("Java", "UML", 1, "Full Model"): "HA-Siala/Java-UML-full-v0.1",
   ("Java", "UML", 2, "Full Model"): "HA-Siala/Java-UML-full-v0.2",
   ("Java", "UML", 3, "Full Model"): "HA-Siala/Java-UML-full-v0.3",
   # Python UML
   ("Python", "UML", 1, "Full Model"): "HA-Siala/Python-UML-full-v0.1",
   ("Python", "UML", 2, "Full Model"): "HA-Siala/Python-UML-full-v0.2",
   ("Python", "UML", 3, "Full Model"): "HA-Siala/Python-UML-full-v0.3",
   # Java OCL
   ("Java", "OCL", 1, "Full Model"): "HA-Siala/Java-OCL-full-v0.1",
   ("Java", "OCL", 2, "Full Model"): "HA-Siala/Java-OCL-full-v0.2",
   # Python OCL
   ("Python", "OCL", 1, "Full Model"): "HA-Siala/Python-OCL-full-v0.1",
   ("Python", "OCL", 2, "Full Model"): "HA-Siala/Python-OCL-full-v0.2",
}
# ------------------------------------------------------------
MODEL_LOCK = threading.Lock()
INFERENCE_LOCK = threading.Lock()
MODEL = None
TOKENIZER = None
MODEL_INFO = None
# ------------------------------------------------------------
def _clear_cuda_cache():
   if torch.cuda.is_available():
      torch.cuda.empty_cache()
# ------------------------------------------------------------
def unload_model():
   global MODEL
   global TOKENIZER
   global MODEL_INFO
   MODEL = None
   TOKENIZER = None
   MODEL_INFO = None
   gc.collect()
   if torch.cuda.is_available():
      torch.cuda.empty_cache()
      try:
         torch.cuda.ipc_collect()
      except Exception:
         pass
# ------------------------------------------------------------
def _get_checkpoint(language, task, version, model_type):  
   key = (language, task, int(version), model_type)
   if model_type == "LoRA Adapter":
      checkpoint = MISTRAL_LORA_CHECKPOINTS.get(key)
   else:
      checkpoint = MISTRAL_FULL_CHECKPOINTS.get(key)
   if checkpoint is None:
      raise ValueError("No Mistral checkpoint configured for: " f"{key}")
   return checkpoint
# ------------------------------------------------------------
def _load_mistral(language, task, version, model_type):
   checkpoint = _get_checkpoint(language=language, task=task, version=version, model_type=model_type)
# ------------------------------------------------------------
   if model_type == "LoRA Adapter":
      tokenizer = AutoTokenizer.from_pretrained(MISTRAL_BASE_MODEL, use_fast=True)
   else:
      tokenizer = AutoTokenizer.from_pretrained(checkpoint, use_fast=True)
   tokenizer.pad_token = tokenizer.unk_token
   tokenizer.padding_side = "left"
# ------------------------------------------------------------
   if model_type == "LoRA Adapter":
      base_model = AutoModelForCausalLM.from_pretrained(
         MISTRAL_BASE_MODEL,
         torch_dtype=torch.bfloat16,
         device_map="auto",
      )
      model = PeftModel.from_pretrained(
         base_model,
         checkpoint,
         torch_dtype=torch.bfloat16,
         is_trainable=False,
      )
   else:
      model = AutoModelForCausalLM.from_pretrained(
         checkpoint,
         torch_dtype=torch.bfloat16,
         device_map="auto",
         low_cpu_mem_usage=True,
      )
   model.eval()
   return (model, tokenizer, checkpoint)
# ------------------------------------------------------------
def load_model(language, task, version, model_type):
   global MODEL
   global TOKENIZER
   global MODEL_INFO
   with MODEL_LOCK:
      unload_model()
      model, tokenizer, checkpoint = _load_mistral(
         language=language,
         task=task,
         version=version,
         model_type=model_type,
      )
      MODEL = model
      TOKENIZER = tokenizer
      MODEL_INFO = {
         "model_family": "Mistral",
         "language": language,
         "task": task,
         "version": int(version),
         "model_type": model_type,
         "checkpoint": checkpoint,
      }
      return MODEL_INFO.copy()
# ------------------------------------------------------------
def is_model_loaded():
   return MODEL is not None
# ------------------------------------------------------------
def get_loaded_model_info():
   if MODEL_INFO is None:
      return None
   return MODEL_INFO.copy()
# ------------------------------------------------------------
def _get_instruction(language, task):
   if language == "Java" and task == "UML":
      return """Generate a concise UML class diagram for the provided Java code. The output should:
1. Define each class and interface only once, including its attributes, methods, and relationships.
2. Include all relationships (Inheritance, Realization, Dependency, Association, Composition, Aggregation) without duplication.
3. Avoid redundant or repeated operations, classes, or relationships."""
# ------------------------------------------------------------
   if language == "Python" and task == "UML":
      return """Generate a concise UML class diagram for the provided Python code. The output should:
1. Define each class and interface only once, including its attributes, methods, and relationships.
2. Include all relationships (Inheritance, Realization, Dependency, Association, Composition, Aggregation) without duplication.
3. Avoid redundant or repeated operations, classes, or relationships."""
# ------------------------------------------------------------
   if language == "Java" and task == "OCL":
      return """Generate an Object Constraint Language (OCL) specification for the provided Java code. The output should:
1. Ensure no repeated or redundant operations or classes.
2. Include only the OCL code for the provided Java code.
3. Do not include statements for items not found in the Java code."""
# ------------------------------------------------------------
   if language == "Python" and task == "OCL":
      return """Generate an Object Constraint Language (OCL) specification for the provided Python code. The output should:
1. Ensure no repeated or redundant operations or classes.
2. Include only the OCL code for the provided Python code.
3. Do not include statements for items not found in the Python code."""
   raise ValueError(f"Unsupported language/task combination: " f"{language}/{task}")
# ------------------------------------------------------------
def generate_prompt(language, task, content):
   instruction = _get_instruction(language=language, task=task)
   prompt = f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response, which is in JSON format that appropriately solves the following Task:

### Instruction:
{instruction}

### Input:
{content}

### Response:
"""
   return prompt
# ------------------------------------------------------------
def generate_inference_output(content, return_metrics=False):
   global MODEL
   global TOKENIZER
   global MODEL_INFO
   if MODEL is None or TOKENIZER is None:
      raise RuntimeError("No model is loaded.")
   if MODEL_INFO is None:
       raise RuntimeError("Model information is unavailable.")
   with INFERENCE_LOCK:
       start_time = time.time()
# ------------------------------------------------------------
       TOKENIZER.pad_token = TOKENIZER.unk_token
       prompt = generate_prompt(
          language=MODEL_INFO["language"],
          task=MODEL_INFO["task"],
          content=content,
       )
       inputs = TOKENIZER(
          prompt,
          return_tensors="pt",
       ).to(DEVICE)
       input_tokens = inputs["input_ids"].shape[1]
       torch.cuda.empty_cache()
# ------------------------------------------------------------
       with torch.inference_mode():
          outputs = MODEL.generate(
             **inputs,
             max_new_tokens=32768,
             temperature=0.2,
             do_sample=True,
             pad_token_id=TOKENIZER.eos_token_id,
             top_p=0.9,
          )
          output_p = TOKENIZER.batch_decode(
             outputs,
             skip_special_tokens=True,
          )
          if output_p:
             output_text = output_p[0]
             split_text_p = output_text.split("Response:")
             if len(split_text_p) > 1:
                cleaned = split_text_p[1]
                cleaned = cleaned.split("###")[0].strip()
                raw_output = cleaned
             else:
                raw_output = None
          else:
             raw_output = None
       inference_time = time.time() - start_time
       if outputs is not None:
          generated_tokens = max(0, outputs.shape[1] - input_tokens)
       else:
          generated_tokens = 0
       result = (
          raw_output,
          input_tokens,
          generated_tokens,
          inference_time,
       )
# ------------------------------------------------------------
       del inputs
       if outputs is not None:
          del outputs
       gc.collect()
       if torch.cuda.is_available():
          torch.cuda.empty_cache()
       if return_metrics:
          return result
       return raw_output
# ------------------------------------------------------------
def _extract_json_text(text):
   if text is None:
      raise ValueError("Empty model output.")
   text = str(text).strip()
   if not text:
      raise ValueError("Empty model output.")
   if text.startswith("```json"):
      text = text[len("```json"):].strip()
   elif text.startswith("```"):
      text = text[3:].strip()
   if text.endswith("```"):
      text = text[:-3].strip()
   return text
# ------------------------------------------------------------
def extract_json_output(text):
   cleaned = _extract_json_text(text)
   try:
      data = ast.literal_eval(cleaned)
      if isinstance(data, dict):
         return data
   except Exception:
      pass
   try:
      data = json.loads(cleaned)
      if isinstance(data, dict):
         return data
   except Exception:
      pass
   first_brace = cleaned.find("{")
   last_brace = cleaned.rfind("}")
   if first_brace >= 0 and last_brace > first_brace:
      candidate = cleaned[first_brace:last_brace + 1]
      try:
         data = ast.literal_eval(candidate)
         if isinstance(data, dict):
            return data
      except Exception:
         pass
      try:
         data = json.loads(candidate)
         if isinstance(data, dict):
            return data
      except Exception:
         pass
   raise ValueError(
        "Could not parse model output as JSON/dictionary."
   )
# ------------------------------------------------------------
def dealing_with_slashes_in_python(text):
   result = re.sub(r"= *'([^']*)'", r'=\\\"\1\\\"', text)
   result1 = re.sub(r"\('([^']*?)'\)", lambda m: r'(\\"' + m.group(1) + r'\\")', result)
   result2 = re.sub(r"\(\\'([^']*?)\\'\)", lambda m: r'(\\"' + m.group(1) + r'\\")', result1)
   return result2
# ------------------------------------------------------------
def is_type_referencing_class(typeprint, class_names):
   for class_name in class_names:
      if class_name in typeprint:
         return True
   return False
# ------------------------------------------------------------
def postprocess_json_file(uml):
   class_names = {cls["name"] for cls in uml}
   for cls in uml:
      cls["variables"] = [var for var in cls.get("variables", []) if not is_type_referencing_class(var.get("typeprint", ""), class_names)]
   return uml
# ------------------------------------------------------------
def replace_type_with_typeprint(obj):
   if isinstance(obj, dict):
      new_obj = {}
      for key, value in obj.items():
          new_key = ("typeprint" if key in ["type", "typePrint"] else key)
          new_obj[new_key] = (replace_type_with_typeprint(value))
      return new_obj
   elif isinstance(obj, list):
      return [replace_type_with_typeprint(item) for item in obj]
   else:
      return obj
# ------------------------------------------------------------
def split_uml_json(data, root):
   data = json.loads(data)
   data = replace_type_with_typeprint(data)
   classes = data.get("classes", [])
   classes = postprocess_json_file(classes)
   relationships = data.get("relationships", [])
   uml_file = os.path.join(root, "Test1.UML")
   rel_file = os.path.join(root, "Test1.REL")
   with open(uml_file, "w", encoding="utf-8") as uml_output:
      json.dump(classes, uml_output, indent=4)
   with open(rel_file, "w", encoding="utf-8") as rel_output:
      json.dump(relationships, rel_output, indent=4)
   return uml_file, rel_file
# ------------------------------------------------------------
def normalize_uml_keys(data_dict):
   normalized = {}
   for key, value in data_dict.items():
      key = str(key).strip()
      if re.match(r"^[12]\s*classes$", key, re.IGNORECASE):
         key = "classes"
      elif re.match(r"^[12]\s*relationships$", key, re.IGNORECASE):
         key = "relationships"
      elif key.lower() == "classes":
         key = "classes"
      elif key.lower() == "relationships":
         key = "relationships"
      normalized[key] = value
   return normalized
# ------------------------------------------------------------
def post_process_uml(input_file, output_directory, language):
   with open(input_file, "r", encoding="utf-8") as file:
      output = file.read()
# ------------------------------------------------------------
   if language == "Python":
      output = dealing_with_slashes_in_python(output)
      output = output.replace("\\'", '\\"')
      output = re.sub(r'\bf"', '"', output)
# ------------------------------------------------------------
   try:
      data_dict = ast.literal_eval(output)
      data_dict = normalize_uml_keys(data_dict)
      if isinstance(data_dict.get("classes"), str):
         data_dict["classes"] = json.loads(data_dict["classes"])
      if isinstance(data_dict.get("relationships"), str):
         data_dict["relationships"] = json.loads(data_dict["relationships"])
# ------------------------------------------------------------
      output_cleaned = json.dumps(data_dict, indent=4)
      uml_file, rel_file = split_uml_json(output_cleaned, output_directory)
      return {
         "success": True,
         "uml_file": uml_file,
         "rel_file": rel_file,
         "data": data_dict,
      }
   except Exception as exc:
      return {
         "success": False,
         "error": str(exc),
      }
# ------------------------------------------------------------
def clean_ocl(lines):
    text = "".join(lines)
    while True:
       old_text = text
       text = re.sub(r';[ \t]*;', ';', text)
       text = re.sub(r';[ \t]*else', 'else', text)
       text = re.sub(r';[ \t]*skip', '', text)
       text = re.sub(r'skip[ \t]*;', '', text)
       text = re.sub(r'\([ \t]*skip[ \t]*;', '(', text)
       text = re.sub(r'skip[ \t]*;[ \t]*\(', '(', text)
       text = re.sub(r';[ \t]*\)', ')', text)
       if text == old_text:
          break
   return text.strip()
# ------------------------------------------------------------
def process_ocl_file(input_file, output_file):
   with open(input_file, "r", encoding="utf-8") as file:
      lines = file.readlines()
   cleaned = clean_ocl(lines)
   with open(output_file, "w", encoding="utf-8") as file:
      file.write(cleaned)
   return output_file
# ------------------------------------------------------------
def post_process_ocl(input_file, output_directory):
   output_file = os.path.join(output_directory, "Test1.OCL")
   try:
      process_ocl_file(input_file, output_file)
      return {
         "success": True,
         "ocl_file": output_file,
      }
   except Exception as exc:
      return {
         "success": False,
         "error": str(exc),
      }
# ------------------------------------------------------------
def format_time(seconds):
   hours = int(seconds // 3600)
   minutes = int((seconds % 3600) // 60)
   remaining_seconds = (seconds % 60)
   result = ""
   if hours > 0:
      result += f"{hours}h "
   if minutes > 0 or hours > 0:
      result += f"{minutes}m "
   result += (f"{remaining_seconds:.6f}s")
   return result
# ------------------------------------------------------------
def create_metrics_text(language, task, model_type, model_version, input_tokens, generated_tokens, inference_time):
   if input_tokens > 0:
      time_per_input_token = (inference_time / input_tokens)
   else:
      time_per_input_token = 0.0
   if generated_tokens > 0:
      time_per_generated_token = (inference_time / generated_tokens)
   else:
      time_per_generated_token = 0.0
   return (
      "===========================================\n"
      "Inference Metrics\n"
      "===========================================\n"
      f"Language:                  {language}\n"
      f"Task:                      {task}\n"
      f"Model type:                {model_type}\n"
      f"Model version:             {model_version}\n"
      f"Input tokens:              {input_tokens}\n"
      f"Generated tokens:          {generated_tokens}\n"
      f"Inference time:            "
      f"{format_time(inference_time)}\n"
      f"Time per input token:      "
      f"{format_time(time_per_input_token)}\n"
      f"Time per generated token:  "
      f"{format_time(time_per_generated_token)}\n"
      "===========================================\n"
   )
# ------------------------------------------------------------
