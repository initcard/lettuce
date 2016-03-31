
# The character Class is the main container for all information relevant to the character.  It takes the parameter from
# the xml element tree and then builds the character from that.  It calls on two other classes, collection and
# mayaObjects.  These should not be constructed directly.  If the xml dom is not formatted correctly, this will fail.
# Setter functions are not necessary since the object is constructed from the xml and should not be changed through this
# script.  Except for the current variables which are switched for the UI.
# **********************************************************************************************************************
#                                                      Character
# **********************************************************************************************************************


class Character:
    def __init__(self, element):
        self.charName = element.get("name")
        self.charAltName = element.get("altName")

        self.collections = []
        self.mayaObjects = []

        temp_col = element.findall("collection")
        temp_mobj = element.findall("mayaObject")

        if temp_col is not None:
            for col in temp_col:
                self.collections.append(_Collection(col))

        if temp_mobj is not None:
            for mobj in temp_mobj:
                self.mayaObjects.append(_MayaObject(mobj))

        self.current_collection = self.collections[0]
        self.current_mayaObjects = self.mayaObjects[0]

    def __str__(self):
        return "{0}, {1}, {2}, {3}".format(self.charName, self.charAltName, self.collections, self.mayaObjects)

    def __repr__(self):
        return str(self)

    # ---------------------------------------------------
    #                       Getters
    # ---------------------------------------------------

    def get_charName(self):
        return self.charName

    def get_charAltName(self):
        return self.charAltName

    def get_collections(self):
        return self.collections

    def get_mayaObjects(self):
        return self.mayaObjects

    def get_hairMayaFile_by_version(self, version):
        return self._col_by_version(version).hairMayaFile

    def get_xgenFile_by_version(self, version):
        return self._col_by_version(version).get_xgenFile

    def get_default_collection(self):
        for col in self.collections:
            if col.get_version() == "default":
                return col

        # If no matches found
        return self.collections[0]

    def get_default_mayaObjects(self):
        for mobj in self.mayaObjects:
            if mobj.get_version() == "default":
                return mobj

        # If no matches found
        return self.mayaObjects[0]

    def get_current_collection(self):
        return self.current_collection


    def get_current_mayaObjects(self):
        return self.current_mayaObjects

    # ---------------------------------------------------
    #                       Setters
    # ---------------------------------------------------

    def set_current_collection(self, collection_name):
        col = []
        for c in self.collections:
            col.append(c.get_version())
        if collection_name in col:
            for c in self.collections:
                if c.get_version() == collection_name:
                    self.current_collection = c
        else:
            raise NameError("Name: {0} does not match a collection in object{1}.".format(collection_name,
                                                                                         self.charName
                                                                                         ))

    def set_current_mayaObjects(self, mayaObjects):
        self.current_mayaObjects = mayaObjects

    # ---------------------------------------------------
    #                     Helpers
    # ---------------------------------------------------

    def _col_by_version(self, version):
        for col in self.collections:
            if col.get_version() == version:
                return col

        # If no matches found
        return None

    def _mobj_by_version(self, version):
        for mobj in self.mayaObjects:
            if mobj.get_version() == version:
                return mobj

        # If no matches found
        return None

# **********************************************************************************************************************
#                                                  _Collections
# **********************************************************************************************************************


class _Collection:
    def __init__(self, element):
        self._version = element.get("version")

        try:
            self._mayaFile = element.find("mayaFile").text
        except AttributeError:
            self._mayaFile = ""

        try:
            self._xgenFile = element.find("xgenFile").text
        except AttributeError:
            self._mayaFile = ""

        self._hairPlates = []

        temp_hp = element.findall("hairPlate")

        if temp_hp is not None:
            for hp in temp_hp:
                self._hairPlates.append(hp.text)

    def __str__(self):
        return "{0}, {1}, {2}, {3}".format(self._version, self._mayaFile, self._xgenFile, self._hairPlates)

    def __repr__(self):
        return str(self)

    # ---------------------------------------------------
    #                       Getters
    # ---------------------------------------------------

    def get_version(self):
        return self._version

    def get_hairMayaFile(self):
        return self._mayaFile

    def get_xgenFile(self):
        return self._xgenFile

    def get_hairPlates(self):
        return self._hairPlates

# **********************************************************************************************************************
#                                                    _MayaObject
# **********************************************************************************************************************


class _MayaObject:
    def __init__(self, element):
        self._version = element.get("version")

        try:
            self._origMeshFile = element.find("mayaFile").text
        except AttributeError:
            self._origMeshFile = ""

        try:
            self._meshNodeName = element.find("characterMesh").text
        except AttributeError:
            self._meshNodeName = ""

    def __str__(self):
        return "{0}, {1}, {2}".format(self._version, self._meshNodeName, self._origMeshFile)

    def __repr__(self):
        return str(self)

    # ---------------------------------------------------
    #                       Getters
    # ---------------------------------------------------

    def get_version(self):
        return self._version

    def get_origMeshFile(self):
        return self._origMeshFile

    def get_meshNodeName(self):
        return self._meshNodeName

# **********************************************************************************************************************
#                                                    SetPackage
# **********************************************************************************************************************


class SetPackage:
    def __init__(self, node_set, set_name):
        self.node_set = node_set
        self.name = set_name

    def __str__(self):
        return self.set_name

    def __repr__(self):
        return self.set_name

    # ---------------------------------------------------
    #                       Getters
    # ---------------------------------------------------

    def get_node_set(self):
        return self.node_set

    def get_name(self):
        return self.name

# **********************************************************************************************************************
#                                                    Exceptions
# **********************************************************************************************************************


class CharacterError(Exception):
    pass
