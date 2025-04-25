# frozen_string_literal: true

# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

require 'time'

task default: %w[fmt push]

task :push do
  system 'git add .'
  system "git commit -m 'Update #{Time.now}.'"
  system 'git pull'
  system 'git push origin main'
end

task :pull do
  system 'git pull'
end

task :run do
  system 'uv run main.py'
end

task :fmt do
  system 'ruff format .'
end
