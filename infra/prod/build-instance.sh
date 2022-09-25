sudo rm -r [old-folder-name]
package_file=$(find . -name 'name-*')
tar xf "$package_file"
helm upgrade folder-name chart-name --values ./folder-name/values.prod.yaml