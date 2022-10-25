# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: test_case_message.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17test_case_message.proto\x12\tprotos.v1\"\xd1\x01\n\x08TestCase\x12\x33\n\x10test_case_detail\x18\x01 \x01(\x0b\x32\x19.protos.v1.TestCaseDetail\x12\x1e\n\x05steps\x18\x02 \x03(\x0b\x32\x0f.protos.v1.Step\x12\x12\n\nproject_id\x18\x03 \x01(\t\x12\x0f\n\x07team_id\x18\x04 \x01(\r\x12\x0e\n\x06\x66older\x18\x05 \x01(\r\x12\x0f\n\x07\x66\x65\x61ture\x18\x06 \x01(\r\x12*\n\x0b\x61ttachments\x18\x07 \x03(\x0b\x32\x15.protos.v1.Attachment\"\xf3\x01\n\x0eTestCaseDetail\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x10\n\x08priority\x18\x03 \x01(\t\x12\x0c\n\x04type\x18\x04 \x01(\t\x12\x14\n\x0clocalization\x18\x05 \x01(\t\x12\x12\n\ncreated_by\x18\x06 \x01(\r\x12\x15\n\rcreation_date\x18\x07 \x01(\t\x12\x13\n\x0bmodified_by\x18\x08 \x01(\r\x12\x13\n\x0bmodify_date\x18\t \x01(\t\x12\x16\n\x0etest_case_type\x18\n \x01(\t\x12\x0c\n\x04time\x18\x0b \x01(\t\x12\x16\n\x0e\x61utomatability\x18\x0c \x01(\t\"\xeb\x03\n\x0eGlobalStepInfo\x12\x13\n\x0b\x64\x65scription\x18\x01 \x01(\t\x12\x0e\n\x06\x64river\x18\x02 \x01(\t\x12\x11\n\tstep_type\x18\x03 \x01(\t\x12\x15\n\rdata_required\x18\x04 \x01(\x08\x12\x14\n\x0cstep_feature\x18\x05 \x01(\t\x12\x13\n\x0bstep_enable\x18\x06 \x01(\x08\x12\x15\n\rstep_editable\x18\x07 \x01(\x08\x12\x11\n\tcase_desc\x18\x08 \x01(\t\x12\x10\n\x08\x65xpected\x18\t \x01(\t\x12\x14\n\x0cverify_point\x18\n \x01(\x08\x12\x15\n\rstep_continue\x18\x0b \x01(\x08\x12\x11\n\testd_time\x18\x0c \x01(\t\x12\x13\n\x0b\x61utomatable\x18\r \x01(\t\x12\x12\n\ncreated_by\x18\x0e \x01(\t\x12\x14\n\x0c\x63reated_date\x18\x0f \x01(\t\x12\x13\n\x0bmodified_by\x18\x10 \x01(\t\x12\x15\n\rmodified_date\x18\x11 \x01(\t\x12\x12\n\nproject_id\x18\x12 \x01(\t\x12\x0f\n\x07team_id\x18\x13 \x01(\t\x12\x12\n\nalways_run\x18\x14 \x01(\x08\x12\x13\n\x0brun_on_fail\x18\x15 \x01(\x08\x12*\n\x0b\x61ttachments\x18\x16 \x03(\x0b\x32\x15.protos.v1.Attachment\"\xae\x02\n\x04Step\x12\n\n\x02id\x18\x01 \x01(\r\x12\x14\n\x0ctest_case_id\x18\x02 \x01(\t\x12\x0f\n\x07step_id\x18\x03 \x01(\r\x12\x0c\n\x04name\x18\x04 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x05 \x01(\t\x12\x10\n\x08\x65xpected\x18\x06 \x01(\t\x12\x10\n\x08has_data\x18\x07 \x01(\x08\x12\x14\n\x0cverify_point\x18\x08 \x01(\x08\x12\x16\n\x0e\x63ontinue_point\x18\t \x01(\x08\x12\x0c\n\x04time\x18\n \x01(\r\x12\x10\n\x08sequence\x18\x0b \x01(\r\x12\x0c\n\x04type\x18\x0c \x01(\t\x12,\n\tstep_info\x18\r \x01(\x0b\x32\x19.protos.v1.GlobalStepInfo\x12\"\n\x07\x61\x63tions\x18\x0e \x03(\x0b\x32\x11.protos.v1.Action\"z\n\x06\x41\x63tion\x12\n\n\x02id\x18\x01 \x01(\r\x12\x0f\n\x07step_id\x18\x02 \x01(\r\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\"\n\x04rows\x18\x04 \x03(\x0b\x32\x14.protos.v1.ActionRow\x12\x10\n\x08sequence\x18\x05 \x01(\r\x12\x0f\n\x07\x65nabled\x18\x06 \x01(\x08\"7\n\tActionRow\x12\n\n\x02id\x18\x01 \x01(\r\x12\x0c\n\x04\x64\x61ta\x18\x02 \x03(\t\x12\x10\n\x08sequence\x18\x03 \x01(\r\"^\n\nAttachment\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04path\x18\x02 \x01(\t\x12\x13\n\x0buploaded_by\x18\x03 \x01(\x05\x12\x13\n\x0buploaded_at\x18\x04 \x01(\t\x12\x0c\n\x04hash\x18\x05 \x01(\tB\x07Z\x05pb/v1b\x06proto3')



_TESTCASE = DESCRIPTOR.message_types_by_name['TestCase']
_TESTCASEDETAIL = DESCRIPTOR.message_types_by_name['TestCaseDetail']
_GLOBALSTEPINFO = DESCRIPTOR.message_types_by_name['GlobalStepInfo']
_STEP = DESCRIPTOR.message_types_by_name['Step']
_ACTION = DESCRIPTOR.message_types_by_name['Action']
_ACTIONROW = DESCRIPTOR.message_types_by_name['ActionRow']
_ATTACHMENT = DESCRIPTOR.message_types_by_name['Attachment']
TestCase = _reflection.GeneratedProtocolMessageType('TestCase', (_message.Message,), {
  'DESCRIPTOR' : _TESTCASE,
  '__module__' : 'test_case_message_pb2'
  # @@protoc_insertion_point(class_scope:protos.v1.TestCase)
  })
_sym_db.RegisterMessage(TestCase)

TestCaseDetail = _reflection.GeneratedProtocolMessageType('TestCaseDetail', (_message.Message,), {
  'DESCRIPTOR' : _TESTCASEDETAIL,
  '__module__' : 'test_case_message_pb2'
  # @@protoc_insertion_point(class_scope:protos.v1.TestCaseDetail)
  })
_sym_db.RegisterMessage(TestCaseDetail)

GlobalStepInfo = _reflection.GeneratedProtocolMessageType('GlobalStepInfo', (_message.Message,), {
  'DESCRIPTOR' : _GLOBALSTEPINFO,
  '__module__' : 'test_case_message_pb2'
  # @@protoc_insertion_point(class_scope:protos.v1.GlobalStepInfo)
  })
_sym_db.RegisterMessage(GlobalStepInfo)

Step = _reflection.GeneratedProtocolMessageType('Step', (_message.Message,), {
  'DESCRIPTOR' : _STEP,
  '__module__' : 'test_case_message_pb2'
  # @@protoc_insertion_point(class_scope:protos.v1.Step)
  })
_sym_db.RegisterMessage(Step)

Action = _reflection.GeneratedProtocolMessageType('Action', (_message.Message,), {
  'DESCRIPTOR' : _ACTION,
  '__module__' : 'test_case_message_pb2'
  # @@protoc_insertion_point(class_scope:protos.v1.Action)
  })
_sym_db.RegisterMessage(Action)

ActionRow = _reflection.GeneratedProtocolMessageType('ActionRow', (_message.Message,), {
  'DESCRIPTOR' : _ACTIONROW,
  '__module__' : 'test_case_message_pb2'
  # @@protoc_insertion_point(class_scope:protos.v1.ActionRow)
  })
_sym_db.RegisterMessage(ActionRow)

Attachment = _reflection.GeneratedProtocolMessageType('Attachment', (_message.Message,), {
  'DESCRIPTOR' : _ATTACHMENT,
  '__module__' : 'test_case_message_pb2'
  # @@protoc_insertion_point(class_scope:protos.v1.Attachment)
  })
_sym_db.RegisterMessage(Attachment)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z\005pb/v1'
  _TESTCASE._serialized_start=39
  _TESTCASE._serialized_end=248
  _TESTCASEDETAIL._serialized_start=251
  _TESTCASEDETAIL._serialized_end=494
  _GLOBALSTEPINFO._serialized_start=497
  _GLOBALSTEPINFO._serialized_end=988
  _STEP._serialized_start=991
  _STEP._serialized_end=1293
  _ACTION._serialized_start=1295
  _ACTION._serialized_end=1417
  _ACTIONROW._serialized_start=1419
  _ACTIONROW._serialized_end=1474
  _ATTACHMENT._serialized_start=1476
  _ATTACHMENT._serialized_end=1570
# @@protoc_insertion_point(module_scope)
