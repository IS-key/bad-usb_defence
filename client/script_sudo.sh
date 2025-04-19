#!/bin/bash

# Create a launcher script named "run_with_root.sh"
cat > run_with_root.sh << 'EOF'
#!/bin/bash
osascript -e "do shell script \"$PWD/USB\ Monitor\" with administrator privileges"
EOF

chmod +x run_with_root.sh
