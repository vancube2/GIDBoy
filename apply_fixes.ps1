# Apply GIDBoy fixes from .new files
$repo = "C:\Users\DELL\Documents\GIDBoy"
Set-Location $repo

Write-Host "Applying fixed files..."

# Move .new files into place
Move-Item -Path "$repo\api\index.py.new" -Destination "$repo\api\index.py" -Force
Move-Item -Path "$repo\core\session_manager.py.new" -Destination "$repo\core\session_manager.py" -Force
Move-Item -Path "$repo\core\intent_classifier_v2.py.new" -Destination "$repo\core\intent_classifier_v2.py" -Force
Move-Item -Path "$repo\llm_client.py.new" -Destination "$repo\llm_client.py" -Force
Move-Item -Path "$repo\src\app\page.tsx.new" -Destination "$repo\src\app\page.tsx" -Force

# Sync api/core/ from core/
Copy-Item -Path "$repo\core\session_manager.py" -Destination "$repo\api\core\session_manager.py" -Force
Copy-Item -Path "$repo\core\intent_classifier_v2.py" -Destination "$repo\api\core\intent_classifier_v2.py" -Force
Copy-Item -Path "$repo\llm_client.py" -Destination "$repo\api\llm_client.py" -Force

Write-Host "Files applied. Building frontend..."
npm run build

Write-Host "Staging and committing..."
git add -A
git commit -m "fix: orchestration continuity, session roundtrip, free APIs, priority stack"
git push origin main

Write-Host "Done! Check Vercel for deployment."
