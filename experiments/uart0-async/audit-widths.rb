#!/usr/bin/env ruby
# Narrow fail-closed ADL audit for this experiment's explicit structure layout.
# This inventories every wide memory LD; it does not infer arbitrary assembly.
root = File.expand_path('../..', __dir__)
files = %w[../../src/uart0_tx.inc fixture.asm].map { |name| File.join(__dir__, name) }
files.concat(ARGV.map { |path| File.expand_path(path) })
fields = {}
(files + [File.join(root, 'src_startup/globals.asm')]).each do |path|
  File.readlines(path).each do |line|
    if (match = line.match(/^\s*(\w+):\s*(?:DB\s+\d+,\d+,\d+|DS\s+3)(?:\s*;.*)?\s*$/))
      fields[match[1]] = 3
    end
  end
end
count = 0
files.each do |path|
  File.readlines(path).each_with_index do |line, index|
    code = line.split(';', 2).first.strip
    next unless (match = code.match(/^ld\s+(?:\(([^)]+)\),\s*(bc|de|hl|ix|iy|sp)|(bc|de|hl|ix|iy|sp),\s*\(([^)]+)\))$/))
    target = match[1] || match[4]
    if (offset = target.match(/^ix\+(\d+)$/))
      abort "bad descriptor width: #{path}:#{index + 1}" unless [1, 4, 7, 10, 13, 16].include?(offset[1].to_i)
    else
      abort "unresolved 24-bit target #{target}: #{path}:#{index + 1}" unless fields[target] == 3
    end
    count += 1
    puts "#{path.delete_prefix(root + '/')}:#{index + 1}: #{code} -> 3-byte field"
  end
end
abort 'empty audit' if count.zero?
puts "PASS #{count} wide memory instructions resolved; descriptor stride=19, last field=16..18"
