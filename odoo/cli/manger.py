import os, subprocess, sys
import pandas as pd;

class Model:
    def __init__(self,module_path : str, model_name : str):
        self.model_name = model_name;
        self.model_class_name = self.__convert_to_class_name()
        self.file_name = model_name.replace(".","_")
        self.module_path = module_path
        self.model_template_text = self.__py_file_template()
        self.view_template_text = self.view_template()
        self.scurity_data = self.security_file()


    def __convert_to_class_name(self):
        class_name = ""
        for s in self.model_name.split("."):
            s = s[0].upper() + s[1:]
            class_name += s
        return class_name
    
    def __py_file_template(self):
        model_text = f"""
# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class {self.model_class_name}(models.Model):
#     _name = {self.model_name}
#     _description = {self.model_name}

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
"""
        return model_text
    
    def view_template(self):
        view_text = f"""
<odoo>
<data>
    <!-- explicit list view definition -->
    <!--
        <record model="ir.ui.view" id="{{self.model_class_name}}.list">
        <field name="name">{{self.model_class_name}} list</field>
        <field name="model">{{self.model_name}}</field>
        <field name="arch" type="xml">
            <tree>
                <field name="name"/>
                <field name="value"/>
                <field name="value2"/>
            </tree>
        </field>
        </record>
    -->

    <!-- actions opening views on models -->
    <!--
        <record model="ir.actions.act_window" id="{{self.model_class_name}}.action_window">
        <field name="name">{{self.model_class_name}} window</field>
        <field name="res_model">{{self.model_name}}</field>
        <field name="view_mode">tree,form</field>
        </record>
    -->

    <!-- server action to the one above -->
    <!--
        <record model="ir.actions.server" id="{{self.model_class_name}}.action_server">
        <field name="name">{{self.model_class_name}} server</field>
        <field name="model_id" ref="model_{{self.model_class_name}}_{{self.model_class_name}}"/>
        <field name="state">code</field>
        <field name="code">
            action = {{
                "type": "ir.actions.act_window",
                "view_mode": "tree,form",
                "res_model": "{{self.model_name}}",
            }}
        </field>
        </record>
    -->

    <!-- Top menu item -->
    <!--
        <menuitem name="test" id="{{self.model_class_name}}.menu_root"/>
    -->
    <!-- menu categories -->
    <!--
        <menuitem name="Menu 1" id="{{self.model_class_name}}.menu_1" parent="{{self.model_class_name}}.menu_root"/>
        <menuitem name="Menu 2" id="{{self.model_class_name}}.menu_2" parent="{{self.model_class_name}}.menu_root"/>
    -->
    <!-- actions -->
    <!--
        <menuitem name="List" id="{{self.model_class_name}}.menu_1_list" parent="{{self.model_class_name}}.menu_1"
                action="test.action_window"/>
        <menuitem name="Server to list" id="{{self.model_class_name}}" parent="{{self.model_class_name}}.menu_2"
                action="{{self.model_class_name}}.action_server"/>
    -->
</data>
</odoo>
"""
        return view_text

    def security_file(self):
        security_data = {
            "id" : f"access_{self.file_name}",
            "name" : f"{self.model_name}",
            "model_id:id" : f"model_{self.file_name}",
            "group_id:id" : "base.group_user",
            "perm_read" : 1,
            "perm_write" : 1,
            "perm_create" : 1,
            "perm_unlink" : 1
        }
        return security_data
    
    def update_manifest(self):
            manifest_path = f"{self.module_path}/__manifest__.py"
            with open(manifest_path, 'r') as file:
                lines = file.readlines()
            with open(manifest_path, 'w') as file:
                for line in lines:
                    file.write(line) 
                    if "'data': [" in line:  
                        file.write(f"\t\t'views/{self.file_name}.xml',\n")  

    def _structure_checker(self):
        structure = ['views', '__manifest__.py', 'models' , 'security']
        input_module_structure = os.listdir(self.module_path)
        for s in structure:
            if(s not in input_module_structure):
                return False;

        if("ir.model.access.csv" not in os.listdir(f"{self.module_path}/security")):
            return False;

        return True;




    
    def build(self):  
        valid_module = self._structure_checker();  
        if(valid_module != True):
            raise FileNotFoundError("""Something wrong you can use scaffold to generate a module, 
                                    or check the doc for the correct structure 
                                    https://www.odoo.com/documentation/17.0/administration/odoo_sh/getting_started/first_module.html""")
        
        try:
            df = pd.DataFrame([self.scurity_data])
            df.to_csv(f"{self.module_path}/security/ir.model.access.csv", mode='a', index=False , header=False)
        except:
            raise FileNotFoundError(f"Could not found the security file, please check it out. {self.module_path}/security/ir.model.access.csv")
        
        try:

            with open(f"{self.module_path}/models/{self.file_name}.py", 'w') as f:
                subprocess.run(['echo', self.model_template_text], stdout=f)
            
            with open(f"{self.module_path}/views/{self.file_name}.xml", 'w') as f:
                subprocess.run(['echo', self.view_template_text], stdout=f)
            
        except:
            raise Exception("Could Not create Files!")
        
        self.update_manifest();
        print("Everything updated successfully.")