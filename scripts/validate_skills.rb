#!/usr/bin/env ruby
# frozen_string_literal: true

require "yaml"

ROOT = File.expand_path("..", __dir__)
SKILLS_DIR = File.join(ROOT, "skills")

def fail_with(message)
  warn "ERROR: #{message}"
  exit 1
end

fail_with("missing skills directory: #{SKILLS_DIR}") unless Dir.exist?(SKILLS_DIR)

skill_files = Dir.glob(File.join(SKILLS_DIR, "*", "SKILL.md")).sort
fail_with("no skills found under #{SKILLS_DIR}") if skill_files.empty?

skill_files.each do |path|
  text = File.read(path)
  match = text.match(/\A---\n(.*?)\n---\n/m)
  fail_with("missing YAML frontmatter: #{path}") unless match

  frontmatter = YAML.safe_load(match[1])
  fail_with("frontmatter must be a mapping: #{path}") unless frontmatter.is_a?(Hash)
  fail_with("missing name: #{path}") if frontmatter["name"].to_s.strip.empty?
  fail_with("missing description: #{path}") if frontmatter["description"].to_s.strip.empty?

  skill_dir = File.dirname(path)
  openai_yaml = File.join(skill_dir, "agents", "openai.yaml")
  if File.exist?(openai_yaml)
    metadata = YAML.safe_load(File.read(openai_yaml))
    fail_with("agents/openai.yaml must be a mapping: #{openai_yaml}") unless metadata.is_a?(Hash)
    fail_with("agents/openai.yaml missing interface: #{openai_yaml}") unless metadata["interface"].is_a?(Hash)
  end

  Dir.glob(File.join(skill_dir, "scripts", "*.py")).sort.each do |script|
    system("python3", "-m", "py_compile", script)
    fail_with("Python script failed to compile: #{script}") unless $?.success?
  end

  puts "ok #{frontmatter["name"]}"
end
