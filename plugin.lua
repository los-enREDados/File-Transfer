local rdt_ft = Proto.new("RDT-FT",  "Reliable File Transfer")

-- rdt_ft.fields = {}

local field_seqNum = ProtoField.int32("RDT-FT.seqNum", "Sequence Number")
local field_connect = ProtoField.int8("RDT-FT.connect", "Bit connect", base.DEC)
local field_tipo = ProtoField.string("RDT-FT.fin", "Tipo conexion")
local field_fin = ProtoField.int8("RDT-FT.fin", "Bit fin", base.DEC)
local field_error = ProtoField.int8("RDT-FT.error", "Bit error", base.DEC)
local field_payload = ProtoField.bytes("RDT-FT.payload", "Payload")

-- rdt_ft.fields = {field_seqNum, field_connect, field_tipo, field_fin, field_error} --, field_payload}
rdt_ft.fields = {field_seqNum, field_connect, field_tipo, field_fin, field_error, field_payload}


-- the `dissector()` method is called by Wireshark when parsing our packets
function rdt_ft.dissector(buffer, pinfo, tree)
  length = buffer:len()
  if length < 0 then return end

  pinfo.cols.protocol = rdt_ft.name

  local payload_tree = tree:add(rdt_ft, buffer(), "Reliable File Transfer Protocol")

  local seqNum_pos = 0
  local seqNum_len = 4
  local seqNum_buffer = buffer(seqNum_pos, seqNum_len)

  -- payload_tree:add(field_seqNum, seqNum_buffer)
  payload_tree:add_packet_field(field_seqNum, seqNum_buffer, ENC_BIG_ENDIAN)

  local connect_pos = seqNum_pos + seqNum_len
  local connect_len = 1 
  local connect_buffer = buffer(connect_pos, connect_len)
  payload_tree:add(field_connect, connect_buffer)

  local tipo_pos = connect_pos + connect_len
  local tipo_len = 1 
  local tipo_buffer = buffer(tipo_pos, tipo_len)
  local tipo_table = {}
  tipo_table[0] = "Download"
  tipo_table[1] = "Upload"
  local tipo_valor = tipo_buffer:uint()
  local tipo_string = tipo_table[tipo_valor]
  payload_tree:add(field_tipo, tipo_string)

  local fin_pos = tipo_pos + tipo_len
  local fin_len = 1 
  local fin_buffer = buffer(fin_pos, fin_len)
  payload_tree:add(field_fin, fin_buffer)

  local error_pos = fin_pos + fin_len
  local error_len = 1 
  local error_buffer = buffer(error_pos, error_len)
  payload_tree:add(field_error, error_buffer)

  local payload_pos = error_pos + error_len
  local payload_len = length - 4 - 1 - 1 - 1 - 1
  local payload_buffer = buffer(payload_pos, payload_len)
  payload_tree:add(field_payload, payload_buffer)

end

--we register our protocol on UDP port 5005
udp_table = DissectorTable.get("udp.port"):add(5005, rdt_ft)
udp_table = DissectorTable.get("udp.port"):add(5006, rdt_ft)
udp_table = DissectorTable.get("udp.port"):add(5007, rdt_ft)
udp_table = DissectorTable.get("udp.port"):add(5008, rdt_ft)
udp_table = DissectorTable.get("udp.port"):add(5009, rdt_ft)
udp_table = DissectorTable.get("udp.port"):add(50010, rdt_ft)
udp_table = DissectorTable.get("udp.port"):add(50011, rdt_ft)
-- register_postdissector(rdt_ft)
