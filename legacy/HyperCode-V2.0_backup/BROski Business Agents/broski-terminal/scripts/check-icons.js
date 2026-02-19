const fs = require('fs');
const path = require('path');

const projectRoot = path.join(__dirname, '..');
const publicDir = path.join(projectRoot, 'public');
const supportDir = path.join(publicDir, 'support');
const assetsDir = path.join(supportDir, 'assets');

const indexHtmlPath = path.join(supportDir, 'index.html');
const manifestPath = path.join(supportDir, 'manifest.json');

console.log('🔍 Checking for Support Hub icon assets...');

let errors = 0;

function checkFile(filePath, source) {
    const absolutePath = path.join(publicDir, filePath);
    if (fs.existsSync(absolutePath)) {
        console.log(`✅ Found: ${filePath} (referenced in ${source})`);
    } else {
        console.error(`❌ MISSING: ${filePath} (referenced in ${source})`);
        errors++;
    }
}

// Check manifest.json
if (fs.existsSync(manifestPath)) {
    try {
        const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
        if (manifest.icons && Array.isArray(manifest.icons)) {
            manifest.icons.forEach(icon => {
                if (icon.src) {
                    // manifest paths are relative to the manifest usually, or absolute from root
                    // In this project, they seem to be absolute /support/assets/...
                    let iconPath = icon.src;
                    if (iconPath.startsWith('/')) {
                        iconPath = iconPath.substring(1); // remove leading slash for joining
                    } else {
                        // if relative to manifest (which is in /support/), we need to handle that
                        // Assuming they are defined as /support/assets/...
                        iconPath = path.join('support', iconPath);
                    }
                    checkFile(iconPath, 'manifest.json');
                }
            });
        }
    } catch (e) {
        console.error('❌ Error parsing manifest.json:', e.message);
        errors++;
    }
} else {
    console.error('❌ manifest.json not found at', manifestPath);
    errors++;
}

// Check index.html
if (fs.existsSync(indexHtmlPath)) {
    const html = fs.readFileSync(indexHtmlPath, 'utf8');
    const regex = /<link[^>]+href=["']([^"']+)["'][^>]*>/g;
    let match;
    while ((match = regex.exec(html)) !== null) {
        const href = match[1];
        if (href.includes('icon') || href.includes('favicon') || href.includes('apple-touch')) {
            let iconPath = href;
            if (iconPath.startsWith('/')) {
                iconPath = iconPath.substring(1);
            } else {
                iconPath = path.join('support', iconPath);
            }
            checkFile(iconPath, 'index.html');
        }
    }
} else {
    console.error('❌ index.html not found at', indexHtmlPath);
    errors++;
}

console.log('\n----------------------------------------');
if (errors === 0) {
    console.log('🎉 All icon assets verified successfully!');
    process.exit(0);
} else {
    console.error(`⚠️ Found ${errors} missing assets.`);
    process.exit(1);
}
