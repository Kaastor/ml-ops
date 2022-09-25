# remember to build docker images

# TODO automatic images build
# TODO https://stackoverflow.com/questions/8653126/how-to-increment-version-number-in-a-shell-script

# copy helm package to remote instance with access to the cluster
package_file_old=$(find . -name 'name-*')
rm "$package_file_old"
helm package ./../helm/phishing
package_file=$(find . -name 'name-*')
scp -r "$package_file" [login]@[instance-name]:[directory]