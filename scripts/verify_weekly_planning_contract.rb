#!/usr/bin/env ruby
# frozen_string_literal: true

require "yaml"

ROOT = File.expand_path("..", __dir__)

def read(path)
  File.read(File.join(ROOT, path))
end

def load_yaml(path)
  YAML.safe_load(read(path), aliases: true)
end

def assert(condition, message)
  raise message unless condition
end

expected_skills = {
  "evaluate_purchase_fit" => "src/skills/evaluate_purchase_fit.yaml",
  "validate_report_completeness" => "src/skills/validate_report_completeness.yaml",
  "track_weekly_decisions" => "src/skills/track_weekly_decisions.yaml",
  "compare_week_over_week" => "src/skills/compare_week_over_week.yaml",
  "design_weekly_route" => "src/skills/design_weekly_route.yaml"
}

expected_skills.each do |skill_name, path|
  full_path = File.join(ROOT, path)
  assert(File.exist?(full_path), "missing #{path}")

  skill = load_yaml(path)
  assert(skill["name"] == skill_name, "#{path} must be named #{skill_name}")
  assert(skill["description"].to_s.length.positive?, "#{path} must include a description")
  assert(skill["input_schema"].is_a?(Hash), "#{path} must include input_schema")
  assert(skill["execution_logic"].to_s.include?("Do not invent"), "#{path} must preserve uncertainty")
  assert(skill["output_contract"].is_a?(Hash), "#{path} must include output_contract")
end

workflow = load_yaml("src/workflows/weekly_planning.yaml")
nodes = workflow.fetch("nodes")
node_ids = nodes.map { |node| node["id"] }

%w[
  Schema_Precheck
  Normalize_Activities
  Normalize_Vehicles
  Prerequisite_Gate
  Specialized_Analysis_Group
  Executive_Summary
].each do |node_id|
  assert(node_ids.include?(node_id), "workflow missing canonical node #{node_id}")
end

assert(node_ids.index("Schema_Precheck") < node_ids.index("Normalize_Activities"), "schema precheck must run before activity normalization")
assert(node_ids.index("Normalize_Activities") < node_ids.index("Normalize_Vehicles"), "activity normalization must run before vehicle normalization")
assert(node_ids.index("Normalize_Vehicles") < node_ids.index("Prerequisite_Gate"), "vehicle normalization must run before readiness gate")
assert(node_ids.index("Prerequisite_Gate") < node_ids.index("Specialized_Analysis_Group"), "readiness gate must run before specialists")
assert(node_ids.index("Specialized_Analysis_Group") < node_ids.index("Executive_Summary"), "specialists must run before Lester")

skill_names = nodes.flat_map do |node|
  if node["tasks"].is_a?(Array)
    node["tasks"].map { |task| task["skill"] }
  else
    node["skill"]
  end
end.compact

expected_skills.keys.each do |skill_name|
  assert(skill_names.include?(skill_name), "workflow must reference #{skill_name}")
end

specialist = nodes.find { |node| node["id"] == "Specialized_Analysis_Group" }
specialist_skills = specialist.fetch("tasks").map { |task| task["skill"] }
assert(specialist_skills.include?("evaluate_purchase_fit"), "specialist group must run evaluate_purchase_fit")

lester = load_yaml("src/agents/lester.yaml")
%w[compare_week_over_week track_weekly_decisions validate_report_completeness].each do |skill_name|
  assert(lester.fetch("skills").include?(skill_name), "Lester must list #{skill_name}")
end

franklin = load_yaml("src/agents/franklin.yaml")
assert(franklin.fetch("skills").include?("evaluate_purchase_fit"), "Franklin must list evaluate_purchase_fit")

agent14 = load_yaml("src/agents/agent14.yaml")
assert(agent14.fetch("skills").include?("design_weekly_route"), "Agent 14 must list design_weekly_route")

portable_skill = read(".github/skills/gta-weekly-planning/SKILL.md")
%w[
  evaluate_purchase_fit
  validate_report_completeness
  track_weekly_decisions
  compare_week_over_week
  design_weekly_route
].each do |needle|
  assert(portable_skill.include?(needle), "portable skill must mention #{needle}")
end

docs = read("README.md") + read("docs/assistant-usage.md")
assert(docs.include?("exactly 3"), "docs must preserve exactly 3 standard report language")
assert(docs.include?("decision memory"), "docs must document decision memory")
assert(docs.include?("validate_report_completeness"), "docs must mention report completeness validation")

puts "weekly planning contract ok"
