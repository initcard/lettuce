import maya.cmds as mc
import lettuceConfig
import xgenSetup as lxg
import logging
import os
import math


class LettuceUI:

    _winName = 'Lettuce'
    uiWindow = mc.window(t=_winName)

    def __init__(self):
        # Config
        self.config = lettuceConfig.Configuration()

        # Log setup
        self.lg = logging.getLogger("lettuce")
        self.lg.setLevel(eval(self.config.get_log_level()))

        self.log_file = self.config.get_log_file()
        self.fh = logging.FileHandler(self.log_file)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.fh.setFormatter(formatter)
        self.lg.addHandler(self.fh)
        self.lg.info("LettuceUI Starting")

        # XML File
        self.xml_load_state = False
        self.char_xml_file = self.config.get_xml_file()
        self.xml_load_state = self._check_xml_file(self.char_xml_file)

        # Characters
        self.char_in_scene = False
        self.char_in_scene_list = []
        self.char_hair_sets = {}

        # UI Creation
        self.title = "Lettuce UI v{}".format(self.config.get_version())
        self._createUI()
        self.lg.info("UI Created")

    def _createUI(self):

        flg = logging.getLogger("lettuce.createUI")

        if mc.window(self.uiWindow, exists=True):
            mc.deleteUI(self.uiWindow)

        mc.window(self.uiWindow,
                  title="{}".format(self.title),
                  menuBar=True,
                  sizeable=False
                  )

        mc.window(self.uiWindow,
                  widthHeight=(406, 202),
                  edit=True,
                  )

        flg.info("Window Created")

        mc.menu("file_menu",
                parent=self.uiWindow,
                label="File",
                tearOff=False
                )
        mc.menuItem(label="Copy ALL Descriptions",
                    command=lambda *_: self._copy_all_desc()
                    )
        mc.menuItem(label="Import ALL Character's Hair",
                    command=lambda *_: self._import_all_hair()
                    )
        mc.menuItem(label="Delete ALL Character's Hair",
                    command=lambda *_: self._delete_all_hair()
                    )
        mc.menuItem(label="Reload",
                    command=lambda *_: self._reloadUI("masterFrame")
                    )

        mc.menu("edit_menu",
                parent=self.uiWindow,
                label="Edit",
                tearOff=False
                )
        mc.menuItem(label="XML Path",
                    command=lambda *_: self._xml_path_menu()
                    )
        mc.menuItem(label="Log Path",
                    command=lambda *_: self._log_path_menu()
                    )
        mc.menuItem("lg_lvl_menu",
                    label="Log Level",
                    subMenu=True
                    )
        mc.radioMenuItemCollection(parent="lg_lvl_menu")
        mc.menuItem(label="Debug",
                    radioButton=False,
                    command=lambda *_: self._change_logging_level("logging.DEBUG")
                    )
        mc.menuItem(label="Info",
                    radioButton=False,
                    command=lambda *_: self._change_logging_level("logging.INFO")
                    )
        mc.menuItem(label="Warning",
                    radioButton=True,
                    command=lambda *_: self._change_logging_level("logging.WARNING")
                    )
        mc.menuItem(label="Error",
                    radioButton=False,
                    command=lambda *_: self._change_logging_level("logging.ERROR")
                    )
        mc.menuItem(label="Critical",
                    radioButton=False,
                    command=lambda *_: self._change_logging_level("logging.CRITICAL")
                    )

        mc.menu("help_menu",
                parent=self.uiWindow,
                label="Help",
                helpMenu=True
                )
        mc.menuItem(label="Documentation",
                    command=lambda *_: self._documentation()
                    )

        flg.info("Menu Bar Created")

        mc.frameLayout('masterFrame',
                       label='',
                       width=400,
                       labelVisible=False,
                       marginWidth=0
                       )

        flg.info("Master Frame Created")

        if self.xml_load_state:
            flg.info("XML File Loaded")
            self.char_in_scene_list = self._get_characters(self.char_xml_file)

            if len(self.char_in_scene_list) > 0:
                self.char_in_scene = True
                flg.info("Characters verified in Scene")
            else:
                self.char_in_scene = False
                flg.info("Characters verified not in scene")

        if self.char_in_scene:
            flg.info("Creating Character Menus")
            self._create_character_frame(self.char_in_scene_list, "masterFrame")
        else:
            flg.info("Added reload button ")
            mc.button('reloadButton',
                      label="Reload",
                      command=lambda *_: self._reloadUI("masterFrame")
                      )

        # Last UI line

        flg.info("Showing UI...")
        mc.showWindow(self.uiWindow)

    def _change_logging_level(self, level):
        flg = logging.getLogger("lettuce._change_logging_level")
        flg.debug("Changing Log Level to {}".format(level))
        print("Changing Log Level to {}".format(level))
        self.lg.setLevel(eval(level))

    def _get_characters(self, xml_file):

        flg = logging.getLogger("lettuce._get_characters")

        flg.info("Retrieving Characters from XML File: {}".format(xml_file))
        all_chars = lxg.generate_characters(xml_file)
        flg.info("Retrieved {} Characters in XML File".format(len(all_chars)))

        flg.debug("Characters Retrieved: ")
        for c in all_chars:
            flg.debug(c.get_charName())

        scene_chars = lxg.get_scene_characters(all_chars)

        flg.debug("Characters Found: ")
        for c in scene_chars:
            flg.debug(c.get_charName())

        return scene_chars

    def _create_character_frame(self, characters, parent):

        flg = logging.getLogger("lettuce._create_character_frame")

        frames = []
        frame_objects = []

        flg.info("Exactly {} characters".format(len(characters)))

        if len(characters) < 2:
            flg.info("Less than 2 characters")

            name = 'row0'

            flg.info("Created row: {}".format(name))

            frame_row = mc.rowLayout(name,
                                     parent=parent,
                                     width=400,
                                     numberOfColumns=2,
                                     columnWidth2=[200, 200]
                                     )
            frames.append(name)
            frame_objects.append(frame_row)
        else:
            flg.info("More than 2 characters")
            rows_to_make = int(math.ceil(len(characters)*0.5))
            flg.info("Going to create {0} rows to contain {1} characters.".format(rows_to_make,
                                                                                   len(characters)
                                                                                   ))
            for i in range(0, rows_to_make):
                name = 'row{}'.format(i)

                flg.info("Created row: {}".format(name))

                frame_row = mc.rowLayout(name,
                                         parent=parent,
                                         width=400,
                                         numberOfColumns=2,
                                         columnWidth2=[200, 200]
                                         )
                frames.append(name)
                frame_objects.append(frame_row)
                mc.window(self.uiWindow,
                          widthHeight=(406, (rows_to_make * 200) + 2),
                          edit=True,
                          )

        flg.info("Created {} total rows".format(len(frames)))

        index = 0

        for f in frames:
            for c in range(index, len(characters)):
                flg.info("Creating panel: {0}; number {1}; in frame {2}".format(characters[c].get_charName(),
                                                                                 c,
                                                                                 f
                                                                                 ))
                self._create_character_panel(characters[c], f)
                if index % 2 == 1:
                    index += 1
                    break
                index += 1

    def _create_character_panel(self, character, parent):

        flg = logging.getLogger("lettuce._create_character_panel")

        col_layout = "{}_panel".format(character.get_charName())
        root_layout = "{}_frame".format(character.get_charName())

        mc.frameLayout(root_layout,
                       labelVisible=False,
                       parent=parent,
                       width=200,
                       marginWidth=10
                       )

        flg.info("Panel name: {}".format(col_layout))
        mc.columnLayout(col_layout,
                        parent=root_layout,
                        width=180,
                        height=200,
                        enableBackground=True,
                        backgroundColor=[0.3, 0.3, 0.3]
                        )
        mc.text(label="{}".format(character.get_charAltName()),
                width=180,
                align="center",
                font="boldLabelFont"
                )

        mc.text(label=" ")

        hair_drop_down = "{}_hair".format(character.get_charName())

        mc.optionMenu(hair_drop_down,
                      parent=col_layout,
                      width=180,
                      changeCommand=lambda *_: self._collection_menu_change(character, hair_drop_down)
                      )
        for i in character.get_collections():
            mc.menuItem("{0}_{1}".format(hair_drop_down, i.get_version()),
                        label="{}".format(i.get_version()),
                        parent=hair_drop_down
                        )
            flg.info("Creating Menu Item for {}".format(i.get_version()))

        mc.text(label=" ")

        mc.button(label="Copy Description",
                  parent=col_layout,
                  width=180,
                  command=lambda *_: self._copy_desc(character)
                  )
        mc.button(label="Import Hair",
                  parent=col_layout,
                  width=180,
                  command=lambda *_: self._import_hair(character)
                  )
        mc.button(label="Delete Hair",
                  parent=col_layout,
                  width=180,
                  command=lambda *_: self._delete_hair(character)
                  )

    def _copy_all_desc(self):

        flg = logging.getLogger("lettuce._copy_all_desc")
        flg.info("Copying ALL Descriptions")

        if self.xml_load_state:
            lxg.copy_xgen_files(self.char_in_scene_list)
        else:
            flg.warning("Unable to copy descriptions because XML File is not loaded or invalid")

    def _copy_desc(self, character):

        flg = logging.getLogger("lettuce._copy_desc")
        flg.info("Copying Descriptions: {}".format(character.get_charName()))

        if self.xml_load_state:
            lxg.copy_xgen_files([character])
        else:
            flg.warning("Unable to copy descriptions because XML File is not loaded or invalid")

    def _import_all_hair(self):

        flg = logging.getLogger("lettuce._import_all_hair")
        flg.info("Importing ALL Hair")

        if self.xml_load_state:
            set_objects = lxg.import_hairMayaFile(self.char_in_scene_list)
            for c in self.char_in_scene_list:
                lxg.wrap_hair_plates(c)
            for o in set_objects:
                self.char_hair_sets[o.get_name()] = o
        else:
            flg.warning("Unable to import hair because XML File is not loaded or invalid")

    def _import_hair(self, character):

        flg = logging.getLogger("lettuce._import_hair")
        flg.info("Importing Hair for {}".format(character.get_charName))

        if self.xml_load_state:
            set_objects = lxg.import_hairMayaFile([character])
            lxg.wrap_hair_plates(character)
            for o in set_objects:
                self.char_hair_sets[o.get_name()] = o
        else:
            flg.warning("Unable to import hair because XML File is not loaded or invalid")

    def _collection_menu_change(self, character, parent):

        flg = logging.getLogger("lettuce._collection_menu_change")

        menu_item = mc.optionMenu(parent,
                                  value=True,
                                  query=True,
                                  )
        flg.info("Item: {0} currently selected in menu {1}".format(menu_item, parent))

        try:
            character.set_current_collection(menu_item)
            flg.info("Current Collection changed to {}".format(menu_item))
        except NameError as e:
            flg.warning("Could not change current collection")
            flg.warning(e)

    def _delete_all_hair(self):

        flg = logging.getLogger("lettuce._delete_all_hair")
        flg.info("Deleting ALL hair sets")

        if self.xml_load_state:
            if self.char_hair_sets:
                for key in self.char_hair_sets:
                    hair_set = self.char_hair_sets[key].get_name()

                    flg.info("Deleting hair set: {}".format(hair_set))

                    lxg.delete_set(hair_set)
                self.char_hair_sets = {}
            else:
                flg.info("No hair sets currently registered in the scene")
                flg.info("Checking for un-registered sets")
                for c in self.char_in_scene_list:
                    hair_set = "{}_hairSetSystem".format(c.get_charName())

                    flg.info("Deleting hair set: {}".format(hair_set))

                    lxg.delete_set(hair_set)
        else:
            flg.warning("Unable to delete hair because XML File is not loaded or invalid")

    def _delete_hair(self, character):

        flg = logging.getLogger("lettuce._delete_hair")
        flg.info("Deleting hair set: {}".format(character.get_charName()))

        if self.xml_load_state:
            hair_set = "{}_hairSetSystem".format(character.get_charName())

            flg.info("Deleting hair set: {}".format(hair_set))

            lxg.delete_set(hair_set)
        else:
            flg.warning("Unable to delete hair because XML File is not loaded or invalid")

    def _xml_path_menu(self):
        print("Feature unavailable at this time")
        return

    def _log_path_menu(self):
        print("Feature unavailable at this time")
        return

    def _documentation(self):
        mc.launch(webPage="https://github.com/theacb/lettuce/wiki")

    def _reloadUI(self, frame):

        flg = logging.getLogger("lettuce._reloadUI")

        mc.deleteUI(frame)
        flg.info("Deleting UI: {}".format(frame))

        mc.frameLayout('masterFrame',
                       parent=self.uiWindow,
                       label='',
                       width=400,
                       labelVisible=False,
                       marginWidth=0
                       )

        if self.xml_load_state:
            flg.info("XML File Loaded")
            self.char_in_scene_list = self._get_characters(self.char_xml_file)

            if len(self.char_in_scene_list) > 0:
                self.char_in_scene = True
                flg.info("Characters verified in Scene")
            else:
                self.char_in_scene = False
                flg.info("Characters verified not in scene")

        if self.char_in_scene:
            flg.info("Creating Character Menus")
            self._create_character_frame(self.char_in_scene_list, "masterFrame")
        else:
            flg.info("Added reload button ")
            mc.button('reloadButton',
                      label="Reload",
                      command=lambda *_: self._reloadUI("reloadButton")
                      )

    def _check_xml_file(self, xml_file):

        flg = logging.getLogger("lettuce._check_xml_file")

        if os.path.isfile(xml_file) and os.access(xml_file, os.R_OK):
            flg.info("Character XML File located at: {}".format(xml_file))
            return True
        else:
            flg.info("Unable to access Character XML File located at: {}".format(xml_file))
            return False
