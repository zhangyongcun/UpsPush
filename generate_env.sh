#!/bin/bash

# Function to find UPS device and generate .env file
generate_env() {
    echo "Looking for UPS device..."
    
    # Try to find UPS in lsusb output
    local device_info=$(lsusb | grep UPS)
    
    if [ -z "$device_info" ]; then
        echo "UPS device not found. Please make sure it's connected."
        echo "You can run 'lsusb' to list all USB devices."
        exit 1
    fi
    
    # Extract vendor and product IDs and ensure they are 4 digits
    local vendor_id=$(echo $device_info | grep -o "ID [0-9a-fA-F]*:" | cut -d' ' -f2 | tr -d ':')
    local product_id=$(echo $device_info | grep -o ":[0-9a-fA-F]*" | cut -d':' -f2 | tr -d '\n' | tr -d '\r')
    
    echo "Found UPS device:"
    echo "$device_info"
    echo "Vendor ID: 0x$vendor_id"
    echo "Product ID: 0x$product_id"
    
    # Create .env file with device IDs on single lines
    cat > .env << EOF
# UPS Device Configuration
VENDOR_ID=0x$vendor_id
PRODUCT_ID=0x$product_id

# Bark Notification Configuration
BARK_URL=https://api.day.app/YOUR_BARK_KEY
BARK_VOLUME=5  # Volume level for notifications (1-10)

# Application Settings
UPDATE_INTERVAL=2  # seconds between status checks
EOF
    
    echo "Created .env file with device IDs"
}

# Main execution
echo "=== UPS Environment File Generator ==="
echo

# Generate .env file
generate_env

echo
echo "Setup completed successfully!"
echo "Please edit .env file to set your Bark API key and other preferences."
