#!/usr/bin/env bash
# Snapshot a selected EMOS worktree; compile only on Oryx, never access hardware.
set -euo pipefail
cd "$(dirname "$0")/../.."
source_root=$(realpath "${1:?EMOS source worktree required}")
run_id=${2:?Fresh native build ID required}
[[ "$run_id" =~ ^[a-z][a-z0-9-]+$ ]] || exit 1
output="build/uart0-extender/$run_id"
test ! -e "$output"
mkdir -p "$output"
ruby - "$source_root" "$output" <<'RUBY'
require 'digest';require 'json';require 'open3'
root,out=ARGV
files=['main.c','MOS.zdsproj']+Dir.glob(root+'/{src,src_startup,src_fatfs,src_umm_malloc,tools/zds}/**/*').select{|p|File.file?(p)&&!p.end_with?('/source.sha256')}.map{|p|p.delete_prefix(root+'/')}
hashes=files.sort.to_h{|p|[p,Digest::SHA256.file(root+'/'+p).hexdigest]}
File.write(out+'/source.sha256',hashes.map{|p,h|h+'  '+p+"\n"}.join)
commit,status=Open3.capture2('git','-C',root,'rev-parse','HEAD');raise 'source identity missing' unless status.success?
File.write(out+'/source.json',JSON.pretty_generate(source_commit:commit.strip,source_root:root,files:hashes,status:'exploratory native build; no hardware or release qualification')+"\n")
RUBY
tar -cf "$output/source.tar" -C "$source_root" main.c MOS.zdsproj src src_startup src_fatfs src_umm_malloc tools/zds
tar -rf "$output/source.tar" -C "$output" source.sha256 source.json
remote="Agon/mystuff/agon-mos/$output"
ssh -o BatchMode=yes oryx-linuxlite "mkdir -p '$remote' && test ! -e '$remote/source.tar'"
scp -q "$output/source.tar" "oryx-linuxlite:$remote/source.tar"
ssh -o BatchMode=yes oryx-linuxlite "cd '$remote' && tar -xf source.tar && sha256sum --check --quiet source.sha256 && bash tools/zds/remote-build.sh > build.log 2>&1" || {
    scp -q "oryx-linuxlite:$remote/build.log" "$output/build.log"
    tail -n 30 "$output/build.log"
    exit 1
}
ssh -o BatchMode=yes oryx-linuxlite "cd '$remote' && sha256sum --check --quiet source.sha256 && tar -cf artifacts.tar MOS.bin MOS.hex MOS.map image.sha256 tools.sha256 build.log logs source.sha256 source.json"
scp -q "oryx-linuxlite:$remote/artifacts.tar" "$output/artifacts.tar"
tar -xf "$output/artifacts.tar" -C "$output"
printf '%s\n' "$output"
