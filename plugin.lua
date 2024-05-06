function bytes_to_int(str,endian,signed) -- use length of string to determine 8,16,32,64 bits
    local t={str:byte(1,-1)}
    if endian=="big" then --reverse bytes
        local tt={}
        for k=1,#t do
            tt[#t-k+1]=t[k]
        end
        t=tt
    end
    local n=0
    for k=1,#t do
        n=n+t[k]*2^((k-1)*8)
    end
    if signed then
        n = (n > 2^(#t*8-1) -1) and (n - 2^(#t*8)) or n -- if last bit set, negative.
    end
    return n
end


local rdt_ft = Proto.new("RDT-FT",  "Reliable File Transfer")

-- rdt_ft.fields = {}

local field_seqNum = ProtoField.int32("RDT-FT.seqNum", "Sequence Number")
local field_connect = ProtoField.int8("RDT-FT.connect", "Bit connect", base.DEC)
local field_tipo = ProtoField.int8("RDT-FT.fin", "Bit tipo", base.DEC)
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
  -- field_seqNum = bytes_to_int(field_seqNum.valuestring, "big", true)
  payload_tree:add(field_seqNum, seqNum_buffer:le_uint64():tohex())

  local connect_pos = seqNum_pos + seqNum_len
  local connect_len = 1 
  local connect_buffer = buffer(connect_pos, connect_len)
  payload_tree:add(field_connect, connect_buffer)

  local tipo_pos = connect_pos + connect_len
  local tipo_len = 1 
  local tipo_buffer = buffer(tipo_pos, tipo_len)
  payload_tree:add(field_tipo, tipo_buffer)

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
register_postdissector(rdt_ft)
