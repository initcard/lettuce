
# Ryan Roberts - Wrap Deformer
# rr_wrap.py
#
# Description:
#       Ryan Robers created a simple function to create a wrap deformer.
#       The wrap deformer needs a little more than the deform command to get working.
#       Michael Clavan
#       I wanted to have the function also return the deformer to the user.  So, my contributions are pretty minor.
#       I converted the wrap deformer into a pynode object type pm.nt.Wrap.
#       Avery Brown
#       Slightly altered things to take driver and driven as parameters instead of *args.  While this changes the functionality
#       from that in the maya UI, it makes more sense within the code that I am using.  I also made some changes to make things
#       more pep8-ish as pycharm was yelling at me about it.  Changed cmds to mc.  


import maya.cmds as mc
import pymel.core as pm 


def create_wrap(driver, driven, **kwargs):
    
    influence = driver
    surface = driven
    
    shapes = mc.listRelatives(influence, shapes=True)
    influenceShape = shapes[0]

    shapes = mc.listRelatives(surface, shapes=True)
    surfaceShape = shapes[0]

    # create wrap deformer
    weightThreshold = kwargs.get('weightThreshold', 0.0)
    maxDistance = kwargs.get('maxDistance', 1.0)
    exclusiveBind = kwargs.get('exclusiveBind', False)
    autoWeightThreshold = kwargs.get('autoWeightThreshold', True)
    falloffMode = kwargs.get('falloffMode', 0)

    wrapData = mc.deformer(surface, type='wrap')
    wrapNode = wrapData[0]

    mc.setAttr(wrapNode + '.weightThreshold', weightThreshold)
    mc.setAttr(wrapNode + '.maxDistance', maxDistance)
    mc.setAttr(wrapNode + '.exclusiveBind', exclusiveBind)
    mc.setAttr(wrapNode + '.autoWeightThreshold', autoWeightThreshold)
    mc.setAttr(wrapNode + '.falloffMode', falloffMode)

    mc.connectAttr(surface + '.worldMatrix[0]', wrapNode + '.geomMatrix')
    
    # add influence
    duplicateData = mc.duplicate(influence, name=influence + 'Base')
    base = duplicateData[0]
    shapes = mc.listRelatives(base, shapes=True)
    baseShape = shapes[0]
    mc.hide(base)
    
    # create dropoff attr if it doesn't exist
    if not mc.attributeQuery('dropoff', n=influence, exists=True):
        mc.addAttr(influence, sn='dr', ln='dropoff', dv=4.0, min=0.0, max=20.0)
        mc.setAttr(influence + '.dr', k=True)
    
    # if type mesh
    if mc.nodeType(influenceShape) == 'mesh':
        # create smoothness attr if it doesn't exist
        if not mc.attributeQuery('smoothness', n=influence, exists=True):
            mc.addAttr(influence, sn='smt', ln='smoothness', dv=0.0, min=0.0)
            mc.setAttr(influence + '.smt', k=True)

        # create the inflType attr if it doesn't exist
        if not mc.attributeQuery('inflType', n=influence, exists=True):
            mc.addAttr(influence, at='short', sn='ift', ln='inflType', dv=2, min=1, max=2)

        mc.connectAttr(influenceShape + '.worldMesh', wrapNode + '.driverPoints[0]')
        mc.connectAttr(baseShape + '.worldMesh', wrapNode + '.basePoints[0]')
        mc.connectAttr(influence + '.inflType', wrapNode + '.inflType[0]')
        mc.connectAttr(influence + '.smoothness', wrapNode + '.smoothness[0]')

    # if type nurbsCurve or nurbsSurface
    if mc.nodeType(influenceShape) == 'nurbsCurve' or mc.nodeType(influenceShape) == 'nurbsSurface':
        # create the wrapSamples attr if it doesn't exist
        if not mc.attributeQuery('wrapSamples', n=influence, exists=True):
            mc.addAttr(influence, at='short', sn='wsm', ln='wrapSamples', dv=10, min=1)
            mc.setAttr(influence + '.wsm', k=True)

        mc.connectAttr(influenceShape + '.ws', wrapNode + '.driverPoints[0]')
        mc.connectAttr(baseShape + '.ws', wrapNode + '.basePoints[0]')
        mc.connectAttr(influence + '.wsm', wrapNode + '.nurbsSamples[0]')

    mc.connectAttr(influence + '.dropoff', wrapNode + '.dropoff[0]')
    # I want to return a pyNode object for the wrap deformer.
    # I do not see the reason to rewrite the code here into pymel.
    # return wrapNode
    return pm.nt.Wrap(wrapNode)
    
# selected = cmds.ls(sl=True)
# createWrap(selected[0],selected[1])


