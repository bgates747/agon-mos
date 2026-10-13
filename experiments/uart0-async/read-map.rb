#!/usr/bin/env ruby
# Package a native ZDS map for the instruction runner; no source translation.
out = ARGV.fetch(0)
map = File.read(File.join(out, 'driver.map'))
segments = map.scan(/^\s*(UART_DRIVER|UART_FIXTURE)\s+normal data\s+C:([0-9A-F]+)\s+C:([0-9A-F]+)\s+([0-9A-F]+)h\s*$/i)
abort 'expected exactly the two contiguous qualification segments' unless segments.size == 2
driver, fixture = segments.sort_by { |s| s[1].to_i(16) }
base, driver_end = driver[1..2].map { |s| s.to_i(16) }
fixture_base, image_end = fixture[1..2].map { |s| s.to_i(16) }
abort 'unexpected segment layout' unless driver[0] == 'UART_DRIVER' && fixture[0] == 'UART_FIXTURE' && base == 0x040000 && fixture_base == driver_end + 1
segments.each do |s|
  abort 'segment size mismatch' unless s[3].to_i(16) == s[2].to_i(16) - s[1].to_i(16) + 1
end
symbols = map.scan(/^(\w+)\s+C:([0-9A-F]+)\s+(driver|fixture)\s+(UART_DRIVER|UART_FIXTURE)\s*$/i)
abort 'missing or duplicate native definitions' if symbols.empty? || symbols.map(&:first).uniq.size != symbols.size
abort 'symbol outside linked image' unless symbols.all? { |s| (base..image_end).cover?(s[1].to_i(16)) }
File.write(File.join(out, 'symbols.txt'), symbols.sort_by { |s| s[1].to_i(16) }.map { |s| "#{s[1]} T #{s[0]}\n" }.join)
# Intel HEX omits trailing uninitialized DS storage. Materialize the full RAM
# allocation as zero bytes, matching the fixture's cold initialization contract.
path = File.join(out, 'driver.bin')
bytes = File.binread(path)
size = image_end - base + 1
abort 'image exceeds native allocation' if bytes.bytesize > size
File.binwrite(path, bytes.ljust(size, "\0"))
puts "Native ZDS map: base=%06X driver=%d fixture=%d image=%d symbols=%d" % [base, driver_end - base + 1, image_end - fixture_base + 1, size, symbols.size]
