import maya.cmds as mc
import lettuceConfig
import xgenSetup as lxg

config = lettuceConfig.Configuration()


class LettuceUI:

    _winName = 'Lettuce'
    uiWindow = mc.window(t=_winName)
    title = "Lettuce UI v{}".format(config.get_version())

    def __init__(self):
        self.createUI()

    def createUI(self):
        if mc.window(self.uiWindow, exists=True):
            mc.deleteUI(self.uiWindow)

        mc.window(self.uiWindow,
                  title="{}".format(self.title)
                  )

        mc.window(self.uiWindow,
                  widthHeight=(400, 400),
                  edit=True
                  )

        mc.columnLayout(self.uiWindow)
        mc.frameLayout('buttonFrame',
                       label='',
                       width=300,
                       labelVisible=False,
                       marginWidth=2
                       )

        mc.setParent('buttonFrame')
        mc.button(label='Execute',
                  command=lambda *_: self.run_test()
                  )

        # Last UI line

        print "Showing UI..."
        mc.showWindow(self.uiWindow)

    def run_test(self):
        all_chars = lxg.generate_characters(lxg.char_hair_file)
        scene_chars = lxg.get_scene_characters(all_chars)
        lxg.copy_xgen_files(scene_chars)
        lxg.import_hairMayaFile(scene_chars)
        for c in scene_chars:
            lxg.wrap_hair_plates(c)

