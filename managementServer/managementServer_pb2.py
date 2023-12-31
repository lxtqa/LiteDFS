# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: managementServer.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16managementServer.proto\"2\n\nserverInfo\x12\n\n\x02id\x18\x01 \x01(\x05\x12\n\n\x02ip\x18\x02 \x01(\t\x12\x0c\n\x04port\x18\x03 \x01(\x05\"\x16\n\x08serverId\x12\n\n\x02id\x18\x01 \x01(\x05\"\x12\n\x05\x65mpty\x12\t\n\x01\x65\x18\x01 \x01(\x05\".\n\x08lockInfo\x12\x10\n\x08\x63lientId\x18\x01 \x01(\x05\x12\x10\n\x08\x66ilePath\x18\x02 \x01(\t\"\x18\n\x08\x66ilepath\x12\x0c\n\x04path\x18\x01 \x01(\t\"\"\n\x04\x66ile\x12\x0c\n\x04path\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\"\x18\n\x08ma_reply\x12\x0c\n\x04\x64one\x18\x01 \x01(\x08\"\'\n\nserverList\x12\x19\n\x04list\x18\x01 \x03(\x0b\x32\x0b.serverInfo\"\'\n\tlockReply\x12\x0c\n\x04\x64one\x18\x01 \x01(\x08\x12\x0c\n\x04info\x18\x02 \x01(\t\"\x18\n\x08\x66ileList\x12\x0c\n\x04list\x18\x01 \x01(\t2\x9b\x03\n\x10managementServer\x12(\n\x0cserverOnline\x12\x0b.serverInfo\x1a\t.ma_reply\"\x00\x12\'\n\rserverOffline\x12\t.serverId\x1a\t.ma_reply\"\x00\x12%\n\tgetServer\x12\t.filepath\x1a\x0b.serverInfo\"\x00\x12&\n\rgetServerList\x12\x06.empty\x1a\x0b.serverList\"\x00\x12\x1c\n\x02ls\x12\t.filepath\x1a\t.fileList\"\x00\x12\x1e\n\x04tree\x12\t.filepath\x1a\t.fileList\"\x00\x12\x1b\n\x05mkdir\x12\x05.file\x1a\t.ma_reply\"\x00\x12 \n\x06\x64\x65lete\x12\t.filepath\x1a\t.ma_reply\"\x00\x12\x1c\n\x06\x63reate\x12\x05.file\x1a\t.ma_reply\"\x00\x12#\n\x08lockFile\x12\t.lockInfo\x1a\n.lockReply\"\x00\x12%\n\nunlockFile\x12\t.lockInfo\x1a\n.lockReply\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'managementServer_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_SERVERINFO']._serialized_start=26
  _globals['_SERVERINFO']._serialized_end=76
  _globals['_SERVERID']._serialized_start=78
  _globals['_SERVERID']._serialized_end=100
  _globals['_EMPTY']._serialized_start=102
  _globals['_EMPTY']._serialized_end=120
  _globals['_LOCKINFO']._serialized_start=122
  _globals['_LOCKINFO']._serialized_end=168
  _globals['_FILEPATH']._serialized_start=170
  _globals['_FILEPATH']._serialized_end=194
  _globals['_FILE']._serialized_start=196
  _globals['_FILE']._serialized_end=230
  _globals['_MA_REPLY']._serialized_start=232
  _globals['_MA_REPLY']._serialized_end=256
  _globals['_SERVERLIST']._serialized_start=258
  _globals['_SERVERLIST']._serialized_end=297
  _globals['_LOCKREPLY']._serialized_start=299
  _globals['_LOCKREPLY']._serialized_end=338
  _globals['_FILELIST']._serialized_start=340
  _globals['_FILELIST']._serialized_end=364
  _globals['_MANAGEMENTSERVER']._serialized_start=367
  _globals['_MANAGEMENTSERVER']._serialized_end=778
# @@protoc_insertion_point(module_scope)
