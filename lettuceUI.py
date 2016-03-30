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

        # UI Creation
        self.title = "Lettuce UI v{}".format(self.config.get_version())
        self._createUI()
        self.lg.debug("UI Created")

    def _createUI(self):

        flg = logging.getLogger("lettuce.createUI")

        if mc.window(self.uiWindow, exists=True):
            mc.deleteUI(self.uiWindow)

        mc.window(self.uiWindow,
                  title="{}".format(self.title),
                  menuBar=True
                  )

        mc.window(self.uiWindow,
                  widthHeight=(400, 400),
                  edit=True,
                  )

        flg.debug("Window Created")

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
                    command=lambda *_: self._reloadUI()
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

        mc.menu("help_menu",
                parent=self.uiWindow,
                label="Help",
                helpMenu=True
                )
        mc.menuItem(label="Documentation",
                    command=lambda *_: self._documentation()
                    )

        flg.debug("Menu Bar Created")

        mc.frameLayout('masterFrame',
                       label='',
                       width=400,
                       labelVisible=False,
                       marginWidth=2
                       )

        flg.debug("Master Frame Created")

        if self.xml_load_state:
            flg.debug("XML File Loaded")
            self.char_in_scene_list = self._get_characters(self.char_xml_file)

            if len(self.char_in_scene_list) > 0:
                self.char_in_scene = True
                flg.debug("Characters verified in Scene")
            else:
                self.char_in_scene = False
                flg.debug("Characters verified not in scene")

        if self.char_in_scene:
            flg.debug("Creating Character Menus")
            self._create_character_frame(self.char_in_scene_list, "masterFrame")
        else:
            flg.debug("Added reload button ")
            mc.button('reloadButton',
                      label="Reload",
                      command=lambda *_: self._reloadUI("masterFrame")
                      )

        # Last UI line

        flg.debug("Showing UI...")
        mc.showWindow(self.uiWindow)

    def _get_characters(self, xml_file):

        flg = logging.getLogger("lettuce._get_characters")

        flg.debug("Retrieving Characters from XML File: {}".format(xml_file))
        all_chars = lxg.generate_characters(xml_file)
        flg.info("Retrieved {} Characters in XML File".format(len(all_chars)))

        flg.debug("Characters Retrieved: ")
        for c in all_chars :
            flg.debug(c.get_charName())

        scene_chars = lxg.get_scene_characters(all_chars)

        flg.debug("Characters Found: ")
        for c in scene_chars :
            flg.debug(c.get_charName())

        return scene_chars

    def _create_character_frame(self, characters, parent):

        flg = logging.getLogger("lettuce._create_character_frame")

        frames = []
        frame_objects = []

        flg.debug("Exactly {} characters".format(len(characters)))

        if len(characters) < 2:
            flg.debug("Less than 2 characters")

            name = 'row0'

            flg.debug("Created row: {}".format(name))

            frame_row = mc.rowLayout(name,
                                     label='',
                                     parent=parent,
                                     width=400,
                                     labelVisible=False,
                                     marginWidth=2
                                     )
            frames.append(name)
            frame_objects.append(frame_row)
        else:
            flg.debug("More than 2 characters")
            for i in range(0, int(math.ceil(len(characters))*0.5)):
                name = 'row{}'.format(i)

                flg.debug("Created row: {}".format(name))

                frame_row = mc.rowLayout(name,
                                         label='',
                                         parent=parent,
                                         width=400,
                                         labelVisible=False,
                                         marginWidth=2
                                         )
                frames.append(name)
                frame_objects.append(frame_row)

        flg.debug("Created {} total rows".format(len(frames)))

        char = 0

        for f in frames:
            if math.ceil(len(characters))*0.5 < len(frames):
                self._create_character_panel(characters[char], f, False)
                char += 1
                self._create_character_panel(characters[char], f, False)
                char += 1
            else:
                self._create_character_panel(characters[char], f, True)

        return

    def _create_character_panel(self, character, parent, full):

        flg = logging.getLogger("lettuce._create_character_panel")

        root_layout = "{}_panel".format(character.get_charName())
        if full:
            width = 400
        else:
            width = 200
        mc.columnLayout(root_layout,
                        parent=parent,
                        width=width,
                        height=400
                        )
        mc.button("button",
                  label="button",
                  parent=root_layout
                  )

    def _copy_all_desc(self):
        if self.xml_load_state:
            return

    def _import_all_hair(self):
        if self.xml_load_state:
            return

    def _xml_path_menu(self):
        return

    def _log_path_menu(self):
        return

    def _documentation(self):
        return

    def _reloadUI(self, frame):

        flg = logging.getLogger("lettuce._reloadUI")

        mc.deleteUI(frame)

        flg.debug("Deleting button: {}".format(button))

        if self.xml_load_state:
            flg.debug("XML File Loaded")
            self.char_in_scene_list = self._get_characters(self.char_xml_file)

            if len(self.char_in_scene_list) > 0:
                self.char_in_scene = True
                flg.debug("Characters verified in Scene")
            else:
                self.char_in_scene = False
                flg.debug("Characters verified not in scene")

        if self.char_in_scene:
            flg.debug("Creating Character Menus")
            self._create_character_frame(self.char_in_scene_list, "masterFrame")
        else:
            mc.frameLayout('masterFrame',
                           parent=self.uiWindow,
                           label='',
                           width=400,
                           labelVisible=False,
                           marginWidth=2
                           )
            flg.debug("Added reload button ")
            mc.button('reloadButton',
                      label="Reload",
                      command=lambda *_: self._reloadUI("reloadButton")
                      )

    def _check_xml_file(self, xml_file):

        flg = logging.getLogger("lettuce._check_xml_file")

        if os.path.isfile(xml_file) and os.access(xml_file, os.R_OK):
            flg.debug("Character XML File located at: {}".format(xml_file))
            return True
        else:
            flg.debug("Unable to access Character XML File located at: {}".format(xml_file))
            return False
