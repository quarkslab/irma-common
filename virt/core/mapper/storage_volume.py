#
# Copyright (c) 2013-2016 Quarkslab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

import logging
import xmltodict

from virt.core.exceptions import StorageVolumeError

log = logging.getLogger(__name__)


# TODO: create our own mapper based on xpath and the code available at
# http://stackoverflow.com/questions/5661968/
class StorageVolume:

    # ===========
    #  Constants
    # ===========

    # unit constants
    B = "B"
    KB = "KB"
    K = "K"
    KiB = "KiB"
    MB = "MB"
    M = "M"
    MiB = "MiB"
    G = "G"
    GB = "GB"
    GiB = "GiB"
    T = "T"
    TB = "TB"
    TiB = "TiB"
    P = "P"
    PB = "PB"
    PiB = "PiB"
    E = "E"
    EB = "EB"
    EiB = "EiB"

    # device constants
    NONE = "none"
    AUTO = "auto"
    EXT2 = "ext2"
    EXT3 = "ext3"
    EXT4 = "ext4"
    UFS = "ufs"
    ISO9660 = "iso9660"
    UDF = "udf"
    GFS = "gfs"
    GFS2 = "gfs2"
    VFAT = "vfat"
    HFS = "hfs+"
    XFS = "xfs"

    # file constants
    RAW = "raw"
    DIR = "dir"
    BOCHS = "bochs"
    CLOOP = "cloop"
    QCOW = "cow"
    DMG = "dmg"
    ISO = "iso"
    QCOW = "qcow"
    QCOW2 = "qcow2"
    VMDK = "vmdk"
    VPC = "vpc"

    # ================================
    #  Constructor & destructor stuff
    # ================================

    def __init__(self):
        self._name = None
        self._key = None
        self._capacity = None
        self._allocation = None
        self._target = None
        self._source = None
        self._backingstore = None

    # =====================
    #  Setters and getters
    # =====================

    # name
    def _set_name(self, value):
        if not isinstance(value, basestring):
            reason = "'value' field '{0}' is not valid".format(value)
            raise StorageVolumeError(reason)
        self._name = value

    def _get_name(self):
        return self._name
    name = property(_get_name, _set_name)

    # key
    def _set_key(self, value):
        if value and not isinstance(value, basestring):
            reason = "'value' field '{0}' is not valid".format(value)
            raise StorageVolumeError(reason)
        self._key = value

    def _get_key(self):
        return self._key
    key = property(_get_key, _set_key)

    # capacity
    def _set_capacity(self, value):
        # parsing and saving a variables
        size, unit = None, None
        if isinstance(value, (basestring, int)):
            size = int(value)
        elif isinstance(value, dict):
            size = int(value['#text'])
            unit = value.get('@unit', None)
        else:
            reason = "'value' field '{0}' is not valid".format(value)
            raise StorageVolumeError(reason)
        # checks on values
        if unit is not None and \
           unit not in ["B", "K", "KB", "KiB", "M", "MB", "MiB", "G",
                        "GB", "GiB", "T", "TB", "TiB", "P", "PB",
                        "PiB", "E", "EB", "EiB"]:
            reason = "'@unit' field '{0}' is not valid".format(unit)
            raise StorageVolumeError(reason)
        # commiting variable to structure
        self._capacity = {}
        self._capacity["#text"] = size
        if unit:
            self._capacity['@unit'] = unit

    def _get_capacity(self):
        return self._capacity
    capacity = property(_get_capacity, _set_capacity)

    # allocation
    def _set_allocation(self, value):
        # parsing and saving a variables
        size, unit = None, None
        if isinstance(value, (basestring, int)):
            size = int(value)
        elif isinstance(value, dict):
            size = int(value['#text'])
            unit = value.get('@unit', None)
        else:
            reason = "'value' field '{0}' is not valid".format(value)
            raise StorageVolumeError(reason)
        # checks on values
        if unit is not None and \
           unit not in ["B", "K", "KB", "KiB", "M", "MB", "MiB", "G",
                        "GB", "GiB", "T", "TB", "TiB", "P", "PB",
                        "PiB", "E", "EB", "EiB"]:
            reason = "'@unit' field '{0}' is not valid".format(value)
            raise StorageVolumeError(reason)
        # commiting variable to structure
        self._allocation = {}
        self._allocation["#text"] = size
        if unit:
            self._allocation['@unit'] = unit

    def _get_allocation(self):
        return self._allocation
    allocation = property(_get_allocation, _set_allocation)

    # target
    # TODO: understand encryption field and implement it
    def _set_target(self, value):
        # initialization
        path, type, permissions, encryption = None, None, None, None
        # parsing
        if isinstance(value, basestring):
            path = value
        elif isinstance(value, dict):
            path = value['path']
            format = value.get('format', None)
            if format:
                type = format.get('@type', None)
            permissions = value.get('permissions', None)
        else:
            reason = "'value' field '{0}' is not valid".format(value)
            raise StorageVolumeError(reason)

        # saving values into variables
        if not isinstance(path, basestring):
            reason = "'path' field '{0}' is not valid".format(path)
            raise StorageVolumeError(reason)
        if type is not None and type not in sum(
            [["NONE", "AUTO", "EXT2", "EXT3", "EXT4", "UFS", "ISO9660",
              "UDF", "GFS", "GFS2", "VFAT", "HFS", "XFS"],
             ["RAW", "DIR", "BOCHS", "CLOOP", "QCOW", "DMG", "ISO",
              "QCOW", "QCOW2", "VMDK", "VPC"]], []):
            reason = "'type' field '{0}' is not valid".format(type)
            raise StorageVolumeError(reason)
        if permissions:
            if isinstance(permissions, int):
                value = permissions
                permissions = {}
                permissions['mode'] = value
                permissions['owner'] = value
                permissions['group'] = value
            elif isinstance(permissions, dict):
                mode = permissions.pop('mode', None)
                owner = permissions.pop('owner', None)
                group = permissions.pop('group', None)
                label = permissions.pop('label', None)
                permissions = {}
                if mode is not None:
                    permissions['mode'] = mode
                if owner is not None:
                    permissions['owner'] = owner
                if group is not None:
                    permissions['group'] = group
                if label is not None:
                    permissions['label'] = label
            else:
                reason = ("'permissions' field '{0}' ".format(permissions) +
                          "is not valid")
                raise StorageVolumeError(reason)
        # commiting value to a new structure
        self._target = {}
        if path:
            self._target['path'] = path
        if type:
            self._target['format'] = {'@type': type}
        if permissions:
            self._target['permissions'] = permissions

    def _get_target(self):
        return self._target
    target = property(_get_target, _set_target)

    # source
    # TODO: understand extent and implement it
    def _set_source(self, value):
        if not value:
            self._source = None
        # parsing
        path = None
        if isinstance(value, basestring):
            path = value
        elif isinstance(value, dict):
            path = value['path']
        else:
            reason = "'value' field '{0}' is not valid".format(value)
            raise StorageVolumeError(reason)
        # commiting value to structure
        if path:
            self._source = {}
            self._source['path'] = path

    def _get_source(self):
        return self._source
    source = property(_get_source, _set_source)

    # backingstore
    def _set_backingstore(self, value):
        if not value:
            self._backingstore = None
        # parsing
        path, type, permissions = None, None, None
        if isinstance(value, basestring):
            path = value
        elif isinstance(value, dict):
            path = value['path']
            format = value.get('format', None)
            if format:
                type = format.get('@type', None)
            permissions = value.get('permissions', None)
        else:
            reason = "'value' field '{0}' is not valid".format(value)
            raise StorageVolumeError(reason)
        # saving to variables
        if not isinstance(path, basestring):
            reason = "'path' field '{0}' is not valid".format(path)
            raise StorageVolumeError(reason)
        if type is not None and type not in sum(
            [["NONE", "AUTO", "EXT2", "EXT3", "EXT4", "UFS",
              "ISO9660", "UDF", "GFS", "GFS2", "VFAT", "HFS",
              "XFS"],
             ["RAW", "DIR", "BOCHS", "CLOOP", "QCOW", "DMG",
              "ISO", "QCOW", "QCOW2", "VMDK", "VPC"]], []):
            reason = "'type' field '{0}' is not valid".format(type)
            raise StorageVolumeError(reason)
        if permissions:
            if isinstance(permissions, int):
                value = permissions
                permissions = {}
                permissions['mode'] = value
                permissions['owner'] = value
                permissions['group'] = value
            elif isinstance(permissions, dict):
                mode = permissions.pop('mode', None)
                owner = permissions.pop('owner', None)
                group = permissions.pop('group', None)
                label = permissions.pop('label', None)
                permissions = {}
                if mode is not None:
                    permissions['mode'] = mode
                if owner is not None:
                    permissions['owner'] = owner
                if group is not None:
                    permissions['group'] = group
                if label is not None:
                    permissions['label'] = label
            else:
                reason = ("'permissions' field '{0}' ".format(permissions) +
                          "is not valid")
                raise StorageVolumeError(reason)
        # commiting values to structure
        self._backingstore = {}
        if path:
            self._backingstore['path'] = path
        if type:
            self._backingstore['format'] = {'@type': type}
        if permissions:
            self._backingstore['permissions'] = permissions

    def _get_backingstore(self):
        return self._backingstore
    backingstore = property(_get_backingstore, _set_backingstore)

    @staticmethod
    def parse(xml):
        obj = StorageVolume()
        try:
            xml_dict = xmltodict.parse(xml)
            # ignore volume tag
            xml_dict = xml_dict['volume']
            # mandatory fields parsing
            obj.name = xml_dict['name']
            key = xml_dict.get('key', None)
            if key:
                obj.key = key
            obj.capacity = xml_dict['capacity']
            obj.allocation = xml_dict['allocation']
            obj.target = xml_dict['target']
            source = xml_dict.get('source', None)
            if source:
                obj.source = source
            backingstore = xml_dict.get('backingStore', None)
            if backingstore:
                obj.backingstore = backingstore
            return obj
        # error when fetching values
        except KeyError as e:
            raise StorageVolumeError("{0}".format(e))
        # error with xmltodict
        except Exception as e:
            raise StorageVolumeError("{0}".format(e))

    def unparse(self, pretty=False):
        if self.name is None or \
           self.capacity is None or \
           self.allocation is None or \
           self.target is None:
            raise StorageVolumeError("Missing mandatory fields value")
        try:
            xml_dict = {}
            xml_dict['name'] = self.name
            if self.key:
                xml_dict['key'] = self.key
            xml_dict['capacity'] = self.capacity
            xml_dict['allocation'] = self.allocation
            xml_dict['target'] = self.target
            if self.source:
                xml_dict['source'] = self.source
            if self.backingstore:
                xml_dict['backingStore'] = self.backingstore
            buffer = xmltodict.unparse({'volume': xml_dict})
            if pretty:
                try:
                    import xml.dom.minidom
                    nodes = xml.dom.minidom.parseString(buffer)
                    buffer = nodes.toprettyxml()
                except:
                    pass
            return buffer
        # error with xmltodict
        except Exception as e:
            raise StorageVolumeError("{0}".format(e))
