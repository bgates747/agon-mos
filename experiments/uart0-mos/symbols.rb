#!/usr/bin/env ruby
out=ARGV.fetch(0)
map=File.read(File.join(out,'MOS.map'))
constants=map.scan(/^(\w+)\s+([0-9A-F]+) \(User Defined\)\s*$/i)
symbols=map.scan(/^(\w+)\s+[CD]:([0-9A-F]+)\s+\S+\s+\S+\s*$/i)
symbols.concat(constants)
abort 'No production symbols' unless symbols.size > 300
abort 'Duplicate symbols' unless symbols.map(&:first).uniq.size == symbols.size
File.write(File.join(out,'symbols.txt'),symbols.map { |name,addr| "#{addr} T #{name}\n" }.join)
