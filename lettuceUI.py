import maya.cmds as mc
import lettuceConfig
import xgenSetup as lxg
import logging
import os


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
        formatter = logging.Formatter(self.config.get_formatter())
        self.fh.setFormatter(formatter)
        self.lg.addHandler(self.fh)
        self.lg.info("LettuceUI Starting")

        # XML File
        self.xml_load_state = False
        self.char_xml_file = self.config.get_xml_file()
        self.xml_load_state = self._check_xml_file(self.char_xml_file)

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
                  menu=True
                  )

        mc.window(self.uiWindow,
                  widthHeight=(400, 400),
                  edit=True,
                  )

        mc.menu(label="File",
                tearOff=False
                )
        mc.menuItem(label="Copy ALL Descriptions",
                    command=lambda *_: self._copy_all_desc()
                    )
        mc.menuItem(label="Import ALL Character's Hair",
                    command=lambda *_: self._import_all_hair()
                    )

        mc.menu(label="Edit",
                tearOff=False
                )
        mc.menuItem(label="XML Path",
                    command=lambda *_: self._xml_path_menu()
                    )
        mc.menuItem(label="Log Path",
                    command=lambda *_: self._log_path_menu()
                    )

        mc.menu(label="Help",
                helpMenu=True
                )
        mc.menuItem(label="Documentation",
                    command=lambda *_: self._documentation()
                    )
        mc.frameLayout('masterFrame',
                       label='',
                       width=300,
                       labelVisible=False,
                       marginWidth=2
                       )

        if self.xml_load_state:
            scene_chars = self._get_characters(self.char_xml_file)
            self._create_character_frame(scene_chars, "masterFrame")
        else:
            mc.button('reloadButton',
                      label="Reload",
                      command=lambda *_: self._reloadUI("reloadButton")
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
        return

    def _create_character_panel(self, character, parent):
            mc.columnLayout("{} panel".format(character),
                            parent=parent
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

    def _reloadUI(self, button):
        mc.deleteUI(button)
        return

    def _check_xml_file(self, xml_file):

        flg = logging.getLogger("lettuce._check_xml_file")

        if os.path.isfile(xml_file) and os.access(xml_file, os.R_OK):
            flg.debug("Character XML File located at: {}".format(xml_file))
            return True
        else:
            flg.debug("Unable to access Character XML File located at: {}".format(xml_file))
            return False
