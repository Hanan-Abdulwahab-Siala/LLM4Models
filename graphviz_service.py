# ------------------------------------------------------------
"""
Author: Hanan Abdulwahab Siala
Supervisor: Kevin Lano
University: King's College London
Date: 27-09-2026
"""
# ------------------------------------------------------------
import json
import os
import shutil
import subprocess
# ------------------------------------------------------------
DEFAULT_GRAPHVIZ_DOT = ("/users/k20122072/.conda/envs/graphviz-env/bin/dot")
GRAPHVIZ_DOT = os.environ.get("GRAPHVIZ_DOT", DEFAULT_GRAPHVIZ_DOT)
# ------------------------------------------------------------
def check_modifier(modifier):
   if modifier == "public":
      return "+"
   elif modifier == "private":
      return "-"
   elif modifier == "protected":
      return "#"
   return ""
# ------------------------------------------------------------
def simplify_type(type_print):
   if type_print is None:
      return ""
   type_print = str(type_print)
   if type_print.startswith("Set"):
      return "Set"
   elif type_print.startswith("Sequence"):
      return "Sequence"
   elif type_print.startswith("Dict"):
      return "Dict"
   return type_print
# ------------------------------------------------------------
def generate_dot_file_for_relationships(path, json_file):
   relationship_path = os.path.join(path, f"{json_file[:-4]}.REL")
   if not os.path.isfile(relationship_path):
      return ""
   with open(relationship_path, "r", encoding="utf-8") as file:
      relation_data = json.load(file)
   if not isinstance(relation_data, list):
      raise ValueError("The REL file must contain a JSON list.")
   relation_text = ""
   for item in relation_data:
      if not isinstance(item, dict):
         continue
      relationship = item.get("Relationship", "")
      source = str(item.get("Source", ""))
      target = str(item.get("Target", ""))
      if not source or not target:
         continue
      temp = ""
# ------------------------------------------------------------
      if relationship == "Realization":
         temp = f'    "{source}" -> "{target}" [headlabel="", taillabel="", label="", arrowhead="empty", arrowtail="empty", style="dashed", fontname="Helvetica", fontcolor="black", fontsize=10.0, color="red"];\n'
# ------------------------------------------------------------
      elif relationship == "Inheritance":
         temp = f'    "{source}" -> "{target}" [headlabel="", taillabel="", label="", arrowhead="empty", arrowtail="empty", style="", fontname="Helvetica", fontcolor="black", fontsize=10.0, color="red"];\n'
# ------------------------------------------------------------
      elif relationship == "Composition":
         role2 = str(item.get("Role2", ""))
         multiplicity2 = str(item.get("Multiplicity2", ""))
         temp = f'    "{source}" -> "{target}" [headlabel="", taillabel="{role2}    {multiplicity2}", label="", arrowhead="diamond", arrowtail="empty", style="", fontname="Helvetica", fontcolor="black", fontsize=10.0, color="red"];\n'
# ------------------------------------------------------------
      elif relationship == "Aggregation":
         role2 = str(item.get("Role2", ""))
         multiplicity2 = str(item.get("Multiplicity2", ""))
         temp = f'    "{source}" -> "{target}" [headlabel="", taillabel="{role2}    {multiplicity2}", label="", arrowhead="odiamond", arrowtail="empty", style="", fontname="Helvetica", fontcolor="black", fontsize=10.0, color="red"];\n'
# ------------------------------------------------------------
      elif relationship == "Association":
         role1 = str(item.get("Role1", ""))
         role2 = str(item.get("Role2", ""))
         multiplicity1 = str(item.get("Multiplicity1", ""))
         multiplicity2 = str(item.get("Multiplicity2", ""))
         if role1 and role2:
            temp = f'    "{source}" -> "{target}" [headlabel="{role1}    {multiplicity1}", taillabel="{role2}    {multiplicity2}", label="", arrowhead="none", arrowtail="empty", style="", fontname="Helvetica", fontcolor="black", fontsize=10.0, color="red"];\n'
         else:
            temp = f'    "{source}" -> "{target}" [headlabel="{role1}    {multiplicity1}", taillabel="{role2}    {multiplicity2}", label="", arrowhead="vee", arrowtail="empty", style="", fontname="Helvetica", fontcolor="black", fontsize=10.0, color="red"];\n'
# ------------------------------------------------------------
      elif relationship == "Dependency":
         role1 = str(item.get("Role1", ""))
         multiplicity1 = str(item.get("Multiplicity1", ""))
         temp = f'    "{source}" -> "{target}" [headlabel="{role1}    {multiplicity1}", taillabel="", label="", arrowhead="vee", arrowtail="empty", style="dashed", fontname="Helvetica", fontcolor="black", fontsize=10.0, color="red"];\n'
      relation_text += temp
   return relation_text
# ------------------------------------------------------------
def format_parameters(parameters, full_parameters):
   if not parameters:
      return ""
   result = []
   if not isinstance(parameters, list):
      return ""
   for parameter in parameters:
      if not isinstance(parameter, dict):
         continue
      name = parameter.get("name", "")
      parameter_type = parameter.get("typeprint", "")
      parameter_type = simplify_type(parameter_type)
      if full_parameters == "1":
         if name and parameter_type:
            result.append(f"{name}:{parameter_type}")
         elif parameter_type:
            result.append(parameter_type)
         elif name:
            result.append(name)
      elif full_parameters == "2":
         if parameter_type:
            result.append(parameter_type)
      else:
         continue
   return ",".join(result)
# ------------------------------------------------------------
def generate_dot_file_for_classes_and_interfaces(path, json_file, json_file2, detailed=True, full_parameters="0"):
   uml_path = os.path.join(path, json_file)
   rel_path = os.path.join(path, json_file2)
   if not os.path.isfile(uml_path):
      raise FileNotFoundError(f"UML file not found: {uml_path}")
   if not os.path.isfile(rel_path):
      raise FileNotFoundError(f"REL file not found: {rel_path}")
# ------------------------------------------------------------
   with open(uml_path, "r", encoding="utf-8") as file:
      data = json.load(file)
   with open(rel_path, "r", encoding="utf-8") as file:
      data2 = json.load(file)
   if not isinstance(data, list):
      raise ValueError("Test1.UML must contain a JSON list.")
   if not isinstance(data2, list):
      raise ValueError("Test1.REL must contain a JSON list.")
   if not data:
      raise ValueError("The UML file does not contain any data.")
# ------------------------------------------------------------
   existing_names = set()
   for item in data:
      if not isinstance(item, dict):
         continue
      name = item.get("name", "")
      if name:
         existing_names.add(str(name))
   for relation in data2:
      if not isinstance(relation, dict):
         continue
      for key in ["Source", "Target"]:
         name = relation.get(key, "")
         if not name:
            continue
         name = str(name)
         if name not in existing_names:
            if (relation.get("Relationship") == "Realization" and key == "Target"):
               class_interface = "Interface"
            else:
               class_interface = "Class"
            data.append(
               {
                  "name": name,
                  "Visibility": "",
                  "IsStatic": "",
                  "IsAbstract": "",
                  "superclasses": [],
                  "variables": [],
                  "constructors": [],
                  "methods": [],
                  "ClassInterface": class_interface,
               }
            )
            existing_names.add(name)
# ------------------------------------------------------------
   dot_text = """digraph G {
   edge [fontname="Helvetica",fontsize=10,labelfontname="arial",labelfontsize=7,color="red"];
   node [fontname="Helvetica",fontsize=10,shape=record,style=filled,fillcolor="white",color="red"];

   graph [ rankdir=BT ]
   node [ shape=none ]

"""
# ------------------------------------------------------------
   for item in data:
      if not isinstance(item, dict):
         continue
      if item.get("ClassInterface") not in ["Class", "Interface"]:
         continue
      variables = item.get("variables", [])
      constructors = item.get("constructors", [])
      methods = item.get("methods", [])
      if not isinstance(variables, list):
         variables = []
      if not isinstance(constructors, list):
         constructors = []
      if not isinstance(methods, list):
         methods = []
      item["variables"] = variables
      item["constructors"] = constructors
      item["methods"] = methods
# ------------------------------------------------------------
   for item in data:
      if not isinstance(item, dict):
         continue
      if item.get("ClassInterface") not in ["Class", "Interface"]:
         continue
      name = str(item.get("name", "Unknown"))
      class_interface = item.get("ClassInterface", "Class")
      visibility = item.get("Visibility", "")
      is_abstract = item.get("IsAbstract", "")
      is_static = item.get("IsStatic", "")
# ------------------------------------------------------------
      front = f'    "{name}" [label=<' '<table border="0" cellborder="1" cellspacing="0"><tr><td>'
      if class_interface == "Interface":
         front += ('&laquo;interface&raquo;<BR/>')
      class_text = '<b>' + check_modifier(visibility) + '\\N' + '</b>'
      if is_abstract in ["abstract", "abstractABC"]:
         class_text = '<i>' + class_text + '</i>'
      if is_static == "static":
         class_text = '<u>' + class_text + '</u>'
      dot_text += (front + class_text + '</td></tr>\n')
      attributes = ""
      operations = ""
# ------------------------------------------------------------
      if detailed:
         variables = item.get("variables", [])
         if variables:
            first = True
            for variable in variables:
               if not isinstance(variable, dict):
                  continue
               if first:
                  front_variable = '            <tr><td align="left">'
                  first = False
               else:
                  front_variable = '<br align="left"/>'
               visibility_variable = (variable.get("Visibility", ""))
               variable_type = simplify_type(variable.get("typeprint", ""))
               variable_name = str(variable.get("name", ""))
               temp = ' ' + check_modifier(visibility_variable) + ' ' + variable_name + ' : ' + variable_type + ' '
               if variable.get("IsAbstract", "") in ["abstract", "abstractABC"]:
                  temp = '<i>' + temp + '</i>'
               if variable.get("IsStatic", "") == "static":
                  temp = '<u>' + temp + '</u>'
               attributes += (front_variable + temp)
            attributes += ('<br align="left"/></td></tr>\n')
         else:
            attributes += ('<tr><td align="left"></td></tr>\n')
# ------------------------------------------------------------
         constructors = item.get("constructors", [])
         has_constructor = False
         if constructors:
            has_constructor = True
            first = True
            for constructor in constructors:
               if not isinstance(constructor, dict):
                  continue
               if first:
                  front_constructor = '            <tr><td align="left">'
                  first = False
               else:
                  front_constructor = '<br align="left"/>'
               visibility_constructor = (constructor.get("Visibility", ""))
               constructor_name = str(constructor.get("name", name))
               temp = (' ' + check_modifier(visibility_constructor) + ' ' + constructor_name + '(')
               parameter_text = format_parameters(constructor.get("parameters", []), full_parameters)
               temp += (parameter_text + ') ' )
               operations += ( front_constructor + temp )
# ------------------------------------------------------------
         methods = item.get("methods", [])
         if methods:
            if has_constructor:
               first = False
            else:
               first = True
            for method in methods:
               if not isinstance(method, dict):
                  continue
               if first:
                  front_method = '            <tr><td align="left">'
                  first = False
               else:
                  front_method = '<br align="left"/>'
               visibility_method = (method.get("Visibility", ""))
               method_name = str(method.get("name", ""))
               temp = (' ' + check_modifier(visibility_method) + ' ' + method_name + '(')
               parameter_text = format_parameters(method.get("parameters", []), full_parameters)
               temp += parameter_text + ')'
               if full_parameters == "1":
                  return_type = method.get("returnType", "")
                  if isinstance(return_type, list):
                     return_type = "[]"
                  if return_type:
                     temp += (': ' + str(return_type) + ' ')
                  else:
                     temp += ' '
               else:
                  temp += ' '
               if method.get("IsAbstract", "") in ["abstract", "abstractABC"]:
                  temp = '<i>' + temp + '</i>'
               if method.get("IsStatic", "") == "static":
                  temp = '<u>' + temp + '</u>'
               operations += (front_method + temp)
            operations += ('<br align="left"/></td></tr>\n')
         else:
            if has_constructor:
               operations += ('<br align="left"/></td></tr>\n')
            else:
               operations += '            <tr><td align="left"></td></tr>\n'
# ------------------------------------------------------------
      dot_text += (attributes + operations + '        </table>> ];\n')
# ------------------------------------------------------------
   dot_text += ("\n" + generate_dot_file_for_relationships(path, json_file))
   dot_text += "}\n"
# ------------------------------------------------------------
   dot_file = os.path.join(path, f"{json_file[:-4]}.dot")
   with open(dot_file, "w", encoding="utf-8") as file:
      file.write(dot_text)
   return dot_file
# ------------------------------------------------------------
def find_graphviz_dot():
   env_dot = os.environ.get("GRAPHVIZ_DOT")
   if env_dot and os.path.isfile(env_dot):
      return env_dot
   if os.path.isfile(GRAPHVIZ_DOT):
      return GRAPHVIZ_DOT
   system_dot = shutil.which("dot")
   if system_dot:
      return system_dot
   return None
# ------------------------------------------------------------
def render_graphviz(dot_file, output_file, output_format):
   output_format = (output_format.upper())
   if output_format not in {"PNG", "PDF", "SVG"}:
      raise ValueError("Unsupported Graphviz format: " + output_format)
   dot_executable = (find_graphviz_dot())
   if dot_executable is None:
      raise RuntimeError("Graphviz 'dot' executable was not found.\n\n" f"Expected:\n{DEFAULT_GRAPHVIZ_DOT}")
   command = [dot_executable, f"-T{output_format.lower()}", dot_file, "-o", output_file]
   try:
      subprocess.run(command, check=True, capture_output=True, text=True)
   except subprocess.CalledProcessError as exc:
      error_message = (exc.stderr.strip() if exc.stderr else str(exc))
      raise RuntimeError("Graphviz failed.\n\n" f"Command: {' '.join(command)}\n\n" f"{error_message}") from exc
   if not os.path.isfile(output_file):
      raise RuntimeError("Graphviz completed but did not create the output file:\n" + output_file)
   return output_file
# ------------------------------------------------------------
def generate_graphviz_diagram(output_directory, detail="Detailed Class Diagram", parameters="Methods Only", output_format="PNG"):
   output_directory = os.path.abspath(output_directory)
   os.makedirs(output_directory, exist_ok=True)
   uml_file = "Test1.UML"
   rel_file = "Test1.REL"
   uml_path = os.path.join(output_directory, uml_file)
   rel_path = os.path.join(output_directory, rel_file)
   if not os.path.isfile(uml_path):
      return {
         "success": False,
         "error": ("Test1.UML was not found:\n" + uml_path),
      }
   if not os.path.isfile(rel_path):
      return {
         "success": False,
         "error": ("Test1.REL was not found:\n" + rel_path),
      }
# ------------------------------------------------------------
   detailed = (detail == "Detailed Class Diagram")
   if parameters == ("Methods with Parameter Names and Types"):
      full_parameters = "1"
   elif parameters == ("Methods with Parameter Types"):
      full_parameters = "2"
   else:
      full_parameters = "0"
   if not output_format:
      output_format = "PNG"
   output_format = (output_format.upper())
   if output_format not in {"PNG", "PDF", "SVG"}:
      return {
         "success": False,
         "error": ("Invalid output format: " + output_format),
      }
   try:
      dot_file = (
         generate_dot_file_for_classes_and_interfaces(
            path=output_directory,
            json_file=uml_file,
            json_file2=rel_file,
            detailed=detailed,
            full_parameters=full_parameters,
         )
      )
# ------------------------------------------------------------
      output_file = os.path.join(output_directory, f"Test1.{output_format.lower()}")
      render_graphviz(dot_file=dot_file, output_file=output_file, output_format=output_format)
      return {
         "success": True,
         "dot_file": dot_file,
         "output_file": output_file,
         "format": output_format,
      }
   except Exception as exc:
      return {
         "success": False,
         "error": (
             f"{type(exc).__name__}: {exc}"
         ),
      }
# ------------------------------------------------------------
