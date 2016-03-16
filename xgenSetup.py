# Os Import
import os
import sys
import shutil
import xml.etree.cElementTree as ET
import time

# Maya imports
import maya.cmds as mc
import maya.mel as mel

# Inter-module imports
import lettuceConfig
from lettuceClasses import *
import tools

# Temporary helper variables
current_folder = "/Volumes/digm_anfx/SPRJ_cgbirds/_production/scenes/edits/HRD_021/"

# Creates the configurations variable and sets up some other variables based on that
config = lettuceConfig.Configuration()
char_hair_file = config.get_xml_file()


# Generates character objects from the xml file
# Returns a list of all of the character classes

def generate_characters(xml_file):
    xml_tree = ET.parse(xml_file)
    root = xml_tree.getroot()

    character_objs = []
    for child in root:
        character_objs.append(Character(child))

    return character_objs

# Filters the character list by the characters currently referenced into the scene


def get_scene_characters(character_objs):
    char_in_scene = []
    full_ref_list = mc.ls(references=True)

    for char in character_objs:
        for mobj in char.get_mayaObjects():
            for ref in full_ref_list:
                ref_file_name = os.path.normpath(mc.referenceQuery(ref, filename=True))
                if mobj.get_origMeshFile() in ref_file_name:
                    char_in_scene.append(char)
    return char_in_scene

# Copies the (char).xgen files from their original locations to the scene folder


def copy_xgen_files(character):
    current_file_dir = get_scene_folder()
    project_dir = get_project_dir()

    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')

    mc.progressBar(gMainProgressBar,
                   edit=True,
                   beginProgress=True,
                   isInterruptable=True,
                   status='Copying XGen Files ...',
                   maxValue=len(character)
                   )
    step = 0
    for c in character:
        if mc.progressBar(gMainProgressBar, query=True, isCancelled=True):
            break
        collection = c.get_default_collection()
        xg_file = collection.get_xgenFile()
        xg_file_resolved = os.path.join(project_dir, xg_file)
        print "Copying file from: {0} to {1}\r...".format(xg_file_resolved, current_file_dir)
        try:
            print "..."
            shutil.copy2(xg_file_resolved, current_file_dir)
            print "Complete"
        except IOError as e:
            print "..."
            mc.progressBar(gMainProgressBar, edit=True, endProgress=True)
            print "IO Error, copying failed.  {}".format(e)
            break
        step += 1
        mc.progressBar(gMainProgressBar, edit=True, step=step)

    mc.progressBar(gMainProgressBar, edit=True, endProgress=True)

# Imports the maya file containing the hair system into the file


def import_hairMayaFile(character):
    imported_nodes = []

    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')

    mc.progressBar(gMainProgressBar,
                   edit=True,
                   beginProgress=True,
                   isInterruptable=True,
                   status='Importing Hair System ...',
                   maxValue=len(character)
                   )
    step = 0
    for c in character:
        set_name = "{}_hairSetSystem".format(c.get_charName())

        delete_set(set_name)

        if mc.progressBar(gMainProgressBar, query=True, isCancelled=True):
            break
        collection = c.get_default_collection()
        ma_file = collection.get_hairMayaFile()
        new_nodes = mc.file(ma_file,
                            i=True,
                            preserveReferences=True,
                            defaultNamespace=True,
                            returnNewNodes=True,
                            )
        imported_nodes.append(new_nodes)

        mc.sets(new_nodes,
                name=set_name,
                text="Contains the hair setup for {0}.  Created at {1} on {2}.".format(c.get_charName(),
                                                                                       time.strftime("%H:%M:%S"),
                                                                                       time.strftime("%y%m%d")
                                                                                       )
                )

        step += 1
        mc.progressBar(gMainProgressBar, edit=True, step=step)
    mc.progressBar(gMainProgressBar, edit=True, endProgress=True)
    return imported_nodes

# Wrapper for maya's workspace method
# Returns the project directory


def get_project_dir():
    return mc.workspace(q=True, rootDirectory=True)

# Wrapper for maya's file method
# Returns the scene name


def get_scene_folder():
    file_name = mc.file(q=True, sceneName=True)
    if sys.platform == "win32":
        last_slash = file_name.rfind('\\')
    else:
        last_slash = file_name.rfind('/')
    return file_name[:last_slash + 1]


def delete_set(set_name):
    if mc.objExists(set_name):
        mc.select(set_name)
        old_objects = mc.ls(selection=True)
        ref_objects = mc.ls(selection=True, referencedNodes=True)
        ref_del_queue = []
        if len(ref_objects) > 0:
            for o in ref_objects:
                top = mc.referenceQuery(o, referenceNode=True)
                ref_del_queue.append(top)
        if len(ref_del_queue):
            for o in ref_del_queue:
                ref_file = mc.referenceQuery(o, filename=True)
                mc.file(ref_file, removeReference=True)
        for o in old_objects:
            try:
                print "Deleting: {}".format(o)
                mc.delete(o)
            except ValueError as e:
                print "Warning: {}".format(e)
        mc.delete(set_name)


def unlock_nodes(set_name):
    if mc.objExists(set_name):
        for o in mc.sets(set_name, query=True):
            if mc.lockNode(o, query=True):
                print "Unlocking {}".format(o)
                mc.lockNode(o, lock=False)


def save_and_reload_scene():
    current_file = mc.file(save=True)
    mc.file(current_file, ignoreVersion=True, open=True, force=True)


def wrap_hair_plates(character):

    char_mObjs = character.get_current_mayaObjects
    char_col = character.get_current_collection

    char_mesh = search_namespaces(character)
    char_hair_plates = char_col.get_hairPlates

    deformer_input_list = []

    history_list = mc.listHistory(char_mesh)
    filtered_list = node_type_filter(history_list,
                                     "joint",
                                     "animCurveUU",
                                     )
    for n in filtered_list:
        node_attr = mc.listAttr(n, leaf=True)
        if "envelope" in node_attr:
            deformer_input_list.append(n)
    for o in deformer_input_list:
        mc.setAttr("{}.envelope".format(o), 0)

    for hp in char_hair_plates:
        tools.create_wrap(char_mesh, hp,
                          exclusiveBind=True,
                          falloffMode=1
                          )

    for o in deformer_input_list:
        mc.setAttr("{}.envelope".format(o), 1)


# Filters

def node_type_filter(node_list, *filter_types):
    filtered_list = []
    for node in node_list:
        if mc.nodeType(node) not in filter_types:
            filtered_list.append(node)
    return filtered_list

def search_namespaces(character):
    return character.get_meshNodeName()
