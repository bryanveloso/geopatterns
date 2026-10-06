# Usage: ruby -I<upstream>/lib tests/ruby/generate_hashes.rb <upstream> > tests/fixtures/hashes.json
# Needs the `color` gem and a checkout of https://github.com/jasonlong/geo_pattern.
require "digest"
require "json"
require "geo_pattern"

upstream = ARGV.fetch(0)
commit = `git -C #{upstream} rev-parse HEAD`.strip

PATTERNS = %w[
  chevrons concentric_circles diamonds hexagons mosaic_squares nested_squares octagons
  overlapping_circles overlapping_rings plaid plus_signs sine_waves squares tessellation triangles xes
].freeze

STRINGS = [
  "Mastering Markdown", "A string for your consideration.", "x", "", "ünïcödé ✓", "😀",
  "The quick brown fox jumps over the lazy dog", "geopatterns", "a" * 200
] + (0..15).map { |i| "sample-#{i}" }

COLOR_STRINGS = ["Mastering Markdown", "x", "sample-3", "sample-9"].freeze
COLOR_OPTIONS = [{color: "#00ff00"}, {base_color: "#00ff00"}, {base_color: "#fc0"}].freeze
SUBSET_STRINGS = ["Mastering Markdown", "x", "sample-0", "sample-5", "sample-10", "sample-15"].freeze

cases = []
STRINGS.each do |s|
  cases << {string: s}
  PATTERNS.each { |p| cases << {string: s, patterns: [p]} }
end
COLOR_STRINGS.each do |s|
  PATTERNS.each do |p|
    COLOR_OPTIONS.each { |o| cases << {string: s, patterns: [p]}.merge(o) }
  end
end
SUBSET_STRINGS.each { |s| cases << {string: s, patterns: %w[sine_waves xes]} }

entries = cases.map do |c|
  opts = c.reject { |k, _| k == :string }
  opts[:patterns] = opts[:patterns].map(&:to_sym) if opts[:patterns]
  svg = GeoPattern.generate(c[:string], **opts).to_svg
  {args: c, sha256: Digest::SHA256.hexdigest(svg)}
end

puts %({"upstream": "jasonlong/geo_pattern", "commit": "#{commit}", "cases": [)
puts entries.map { |e| "  #{JSON.generate(e)}" }.join(",\n")
puts "]}"
