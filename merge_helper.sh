#!/bin/bash
echo "🔧 Merge-Konflikte werden automatisch als gelöst markiert..."
git add .
git rebase --continue
