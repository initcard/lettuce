# Os Import
import os
import sys
import shutil
import xml.etree.cElementTree as ET
import time
import logging

# Maya imports
import maya.cmds as mc
import maya.mel as mel

# Inter-module imports
from lettuceClasses import *
import tools

# Creates the configurations variable and sets up some other variables based on that
mlg = logging.getLogger("lettuce.xgenSetup")


def generate_characters(xml_file):
    """
    Generates character objects based on the specified xml file
    :param xml_file: A path to the specified xml file
    :return: A list of all of the character objects generated
    """
    flg = logging.getLogger("lettuce.xgenSetup.generate_characters")

    flg.debug("Parsing XML File: {}".format(xml_file))
    xml_tree = ET.parse(xml_file)
    root = xml_tree.getroot()

    flg.info("Generating {} Characters".format(len(root)))
    character_objs = []
    for child in root:
        try:
            char = Character(child)
            flg.debug("Character: {}".format(char))
            character_objs.append(char)
        except AttributeError as e:
            flg.error("Character not created from child, {}".format(child))
            flg.debug("Error: {}".format(e))

    flg.info("Returning {} Characters".format(len(character_objs)))
    return character_objs


def get_scene_characters(character_objs):
    """
    Filters the list of character objects to find which ones are present in the scene
    :param character_objs: A list of character objects defined in the xml file
    :return: A list of all of the defined characters in the scene
    """
    flg = logging.getLogger("lettuce.xgenSetup.get_scene_characters")

    char_in_scene = []
    full_ref_list = mc.ls(references=True)

    flg.info("Checking {} scene references for characters".format(len(full_ref_list)))
    for r in full_ref_list:
        flg.debug(r)

    # TODO: Figure out fatal reference error, scene 04, shot irr_123 is the source

    flg.debug("For char in character_objs")
    for char in character_objs:
        for mobj in char.get_mayaObjects():
            for ref in full_ref_list:
                flg.debug("Querying reference for {0}/{1}/{2}".format(char.get_charName(),
                                                                      mobj.get_version(),
                                                                      ref
                                                                      ))
                try:
                    ref_file_name = os.path.normpath(mc.referenceQuery(ref, filename=True))
                    if mobj.get_origMeshFile() in ref_file_name:
                        flg.info("{} is in scene".format(char))
                        char_in_scene.append(char)
                except RuntimeError as e:
                    flg.warning("Unable to query reference, {}.".format(ref))
                    flg.debug("Error: {}".format(e))

    flg.info("{} characters in scene".format(len(char_in_scene)))
    return char_in_scene

# Copies the (char).xgen files from their original locations to the scene folder


def copy_xgen_files(character):
    """
    Copies xgen files from their central location to the scene folder
    :param character: A list of Character objects to process
    :return: Nothing
    """
    flg = logging.getLogger("lettuce.xgenSetup.copy_xgen_files")

    current_file_dir = get_scene_folder()
    project_dir = get_project_dir()

    flg.debug("Current Scene's folder: {}".format(current_file_dir))
    flg.debug("Current Project's folder: {}".format(project_dir))

    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')

    mc.progressBar(gMainProgressBar,
                   edit=True,
                   beginProgress=True,
                   isInterruptable=True,
                   status='Copying XGen Files ...',
                   maxValue=len(character)
                   )
    step = 0

    flg.info("Copying {} XGen files".format(len(character)))

    for c in character:
        if mc.progressBar(gMainProgressBar, query=True, isCancelled=True):
            flg.info("Progress Interrupted by user")
            flg.debug("Canceled on step: {0} of {1}".format(step, len(character)))
            break
        collection = c.get_default_collection()

        flg.debug("Character: {}".format(c.get_charName()))
        flg.debug("Collection: {}".format(collection))

        xg_file = collection.get_xgenFile()
        xg_file_resolved = os.path.join(project_dir, xg_file)

        flg.debug("Copying file from: {0} to {1}".format(xg_file_resolved, current_file_dir))
        flg.debug("...")
        try:
            shutil.copy2(xg_file_resolved, current_file_dir)
            flg.debug("Complete")
        except IOError as e:
            mc.progressBar(gMainProgressBar, edit=True, endProgress=True)
            flg.error("IO Error, copying failed.  {}".format(e))
            break
        step += 1
        mc.progressBar(gMainProgressBar, edit=True, step=step)

    flg.info("Complete, {} characters copied".format(len(character)))
    mc.progressBar(gMainProgressBar, edit=True, endProgress=True)

# Imports the maya file containing the hair system into the file


def import_hairMayaFile(character):
    """
    Imports the contents of the mayaFiles specified in the collections for the different characters.
    Creates a set containing each hair system imported.  Deletes old hair systems on import to prevent clashing.
    XGen limitations prevent importing with namespaces.
    Uses the maya progress bar in case this takes a long time, which also makes it cancellable with the esc key

    :param character: A list of Character objects to process
    :return: A class object containing nodes that were imported
    """

    flg = logging.getLogger("lettuce.xgenSetup.import_hairMayaFile")

    set_packages = []

    # Maya progress bar setup
    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')

    mc.progressBar(gMainProgressBar,
                   edit=True,
                   beginProgress=True,
                   isInterruptable=True,
                   status='Importing Hair System ...',
                   maxValue=len(character)
                   )
    step = 0

    flg.info("Importing {} hair system files".format(len(character)))

    # For loop allows a list of all characters or a list of a single character for flexibility
    for c in character:
        imported_nodes = []

        # Allows the user to cancel the evaluation of the script
        if mc.progressBar(gMainProgressBar, query=True, isCancelled=True):
            flg.info("Progress Interrupted by user")
            flg.debug("Canceled on step: {0} of {1}".format(step, len(character)))
            flg.debug("Cancelled at beginning of loop")
            break

        flg.debug("Character: {}".format(c.get_charName()))
        set_name = "{}_hairSetSystem".format(c.get_charName())

        flg.debug("Generating character set name: {}".format(set_name))

        delete_set(set_name)

        # Allows the user to cancel the evaluation of the script
        if mc.progressBar(gMainProgressBar, query=True, isCancelled=True):
            flg.info("Progress Interrupted by user")
            flg.debug("Canceled on step: {0} of {1}".format(step, len(character)))
            flg.debug("Cancelled after set sanitization")
            break

        collection = c.get_default_collection()
        ma_file = collection.get_hairMayaFile()

        flg.debug("Collection: {}".format(collection))
        flg.debug("Importing file: {}".format(ma_file))

        new_nodes = mc.file(ma_file,
                            i=True,
                            preserveReferences=True,
                            defaultNamespace=True,
                            returnNewNodes=True,
                            )
        imported_nodes.append(new_nodes)

        flg.debug("Imported Nodes:")
        for n in new_nodes:
            flg.debug(n)

        # Naming the set and setting the description with it's import time.
        mc.sets(new_nodes,
                name=set_name,
                text="Contains the hair setup for {0}.  Created at {1} on {2}.".format(c.get_charName(),
                                                                                       time.strftime("%H:%M:%S"),
                                                                                       time.strftime("%y%m%d")
                                                                                       )
                )

        # Allows the user to cancel the evaluation of the script
        if mc.progressBar(gMainProgressBar, query=True, isCancelled=True):
            flg.info("Progress Interrupted by user")
            flg.debug("Canceled on step: {0} of {1}".format(step, len(character)))
            flg.debug("Cancelled after import")
            break

        flg.debug("Creating return package")
        flg.info("Returning {} hair system nodes".format(len(imported_nodes)))

        package = SetPackage(imported_nodes, set_name)

        set_packages.append(package)

        # Advances the progress bar
        step += 1
        mc.progressBar(gMainProgressBar, edit=True, step=step)

    # Closes the progress bar when complete
    mc.progressBar(gMainProgressBar, edit=True, endProgress=True)

    flg.debug("Returning packages :".format(set_packages))

    return set_packages

# Wrapper for maya's workspace method
# Returns the project directory


def get_project_dir():
    """ Queries maya to find the current project directory """

    flg = logging.getLogger("lettuce.xgenSetup.get_project_dir")

    proj_dir = mc.workspace(q=True, rootDirectory=True)

    flg.debug("Current Project Folder: {}".format(proj_dir))

    return proj_dir

# Wrapper for maya's file method
# Returns the scene name


def get_scene_folder():
    """ Queries Maya to get the folder containing the current scene """

    flg = logging.getLogger("lettuce.xgenSetup.get_scene_folder")

    file_name = mc.file(q=True, sceneName=True)

    flg.debug("Scene fileName: {}".format(file_name))

    if sys.platform == "win32":
        last_slash = file_name.rfind('\\')
    else:
        last_slash = file_name.rfind('/')

    scene_dir = file_name[:last_slash + 1]

    flg.debug("Scene directory: {}".format(scene_dir))

    return scene_dir


def delete_set(set_name):
    """
    Attempts to delete every node in a set, will remove associated references as well
    :param set_name: A string containing the name of a maya set
    :return: Nothing
    """

    flg = logging.getLogger("lettuce.xgenSetup.delete_set")

    flg.debug("Set to delete: {}".format(set_name))

    if mc.objExists(set_name):
        mc.select(set_name)
        old_objects = mc.ls(selection=True)
        flg.debug("Old Objects:")
        for o in old_objects:
            flg.debug(o)
        ref_objects = mc.ls(selection=True, referencedNodes=True)

        ref_del_queue = []
        if len(ref_objects) > 0:
            flg.debug("Old Reference Nodes:")
            for o in ref_objects:
                flg.debug(o)
            for o in ref_objects:
                flg.debug("Queuing {} for reference removal".format(o))
                top = mc.referenceQuery(o, referenceNode=True)
                ref_del_queue.append(top)
        if len(ref_del_queue):
            for o in ref_del_queue:
                flg.debug("Removing reference: {}".format(o))
                ref_file = mc.referenceQuery(o, filename=True)
                mc.file(ref_file, removeReference=True)
        for o in old_objects:
            try:
                flg.debug("Deleting {}".format(o))
                mc.delete(o)
            except ValueError as e:
                flg.warning("Unable to delete {0}.  Error: {1}".format(o, e))
        flg.debug("Deleting set: {}".format(set_name))
        mc.delete(set_name)


def unlock_nodes(set_name):
    """
    Will attempt to unlock every node in a set
    :param set_name: A string containing the name of a maya set
    :return: Nothing
    """

    flg = logging.getLogger("lettuce.xgenSetup.unlock_nodes")

    if mc.objExists(set_name):
        for o in mc.sets(set_name, query=True):
            if mc.lockNode(o, query=True):
                flg.debug("Unlocking {}".format(o))
                mc.lockNode(o, lock=False)
    else:
        flg.warning("Set, {}, does not exist".format(set_name))


def save_and_reload_scene():
    """ Uses Maya file commands to save the current file and reload it """

    flg = logging.getLogger("lettuce.xgenSetup.save_and_reload_scene")

    current_file = mc.file(save=True)
    flg.debug("Current File: {}".format(current_file))
    mc.file(current_file, ignoreVersion=True, open=True, force=True)


def wrap_hair_plates(character):
    """
    Wraps the hairplate objects to the character object
    :param character: a Character object, singular
    :return:
    """

    flg = logging.getLogger("lettuce.xgenSetup.wrap_hair_plates")

    flg.debug("Wrapping hair plates to {}".format(character.get_charName()))

    char_col = character.get_current_collection()
    flg.debug("Current Collection: {}".format(char_col.get_version()))

    char_mesh = search_namespaces_for_mesh(character)
    char_hair_plates = char_col.get_hairPlates()
    flg.debug("Character mesh object: {}".format(char_mesh))
    flg.debug("Character hair plate objects: {}".format(char_hair_plates))

    deformer_input_list = []

    history_list = mc.listHistory(char_mesh)
    flg.debug("Character mesh history nodes: {}".format(history_list))

    filtered_list = node_type_filter(history_list,
                                     "joint",
                                     "animCurveUU",
                                     )
    flg.debug("Character mesh history nodes, filtered: ".format(filtered_list))

    for n in filtered_list:
        print n
        node_attr = mc.listAttr(n, leaf=True)
        if "envelope" in node_attr:
            deformer_input_list.append(n)
    flg.debug("Objects containing envelope attributes: {}".format(deformer_input_list))

    for o in deformer_input_list:
        flg.debug("Setting {0} input {1} envelope to 0".format(char_mesh, o))
        mc.setAttr("{}.envelope".format(o), 0)

    flg.debug("Viewport refresh")
    mc.refresh()

    for hp in char_hair_plates:
        tools.create_wrap(char_mesh, hp,
                          exclusiveBind=True,
                          falloffMode=1,
                          shapeDeformed=True
                          )
        flg.debug("Binding {0} to {1}".format(hp, char_mesh))

    flg.debug("Viewport refresh")
    mc.refresh()

    for o in deformer_input_list:
        flg.debug("Setting {0} input {1} envelope to 1".format(char_mesh, o))
        mc.setAttr("{}.envelope".format(o), 1)


def node_type_filter(node_list, *filter_types):
    """
    Filters a list by type
    :param node_list: A list containing maya nodes
    :param filter_types: *A list of strings that correspond to maya types that need to be filtered out of node_list
    :return: The node_list after it has been filtered of specified node types
    """

    flg = logging.getLogger("lettuce.xgenSetup.node_type_filter")

    flg.debug("Filtering Node List")

    filtered_list = []
    for node in node_list:
        node_type = mc.nodeType(node)
        flg.debug("Node, {0}, is of type, {1}".format(node, node_type))
        if node_type not in filter_types:
            flg.debug("Node kept")
            filtered_list.append(node)
        else:
            flg.debug("Node filtered")
    flg.debug("Returning Filtered List")
    return filtered_list


def search_namespaces_for_mesh(character):
    """
    Searches maya namespaces to find a a character's mesh
    :param character: A Character object, singular
    :return: A string containing the name of the character's mesh or just the name of the character's mesh
    """

    flg = logging.getLogger("lettuce.xgenSetup.search_namespaces_for_mesh")

    flg.debug("Searching namespaces for {}".format(character.get_charName()))

    char_mObjs = character.get_current_mayaObjects()
    char_mesh = char_mObjs.get_meshNodeName()
    flg.debug("Character's maya objects: {}".format(char_mObjs.get_version()))
    flg.debug("Character's mesh object: {}".format(char_mesh))

    full_ref_list = mc.ls(references=True)
    flg.debug("Full scene reference list: ")
    for r in full_ref_list:
        flg.debug(r)

    for ref in full_ref_list:
        try:
            ref_file_name = os.path.normpath(mc.referenceQuery(ref, filename=True))
            if char_mObjs.get_origMeshFile() in ref_file_name:
                flg.debug("Reference file name: ".format(ref_file_name))
                return "{}:{}".format(remove_rn(ref), char_mesh)
        except RuntimeError as e:
            flg.warning("Unable to query reference, {}.".format(ref))
            flg.debug("Error: {}".format(e))

    flg.error("Mesh file, {}, not referenced in this scene.".format(char_mObjs.get_origMeshFile()))
    return ""


def remove_rn(reference_node_name):
    """
    Removes the RN from the end of a reference node's name
    :param reference_node_name: node with a reference prefix
    :return: Node with reference prefix removed
    """

    flg = logging.getLogger("lettuce.xgenSetup.remove_rn")

    last_r = reference_node_name.rfind('R')
    rn_removed = reference_node_name[:last_r]

    flg.debug("Converting {0} to {1}.".format(reference_node_name, rn_removed))
    return rn_removed
