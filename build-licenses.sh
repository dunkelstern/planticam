#!/bin/bash

# make -C output/planticam legal-info

pushd output/planticam/legal-info
rm -rf about
mkdir -p about
find licenses -type f | while read filename ; do
    package=$(echo $filename|sed -e 's@licenses/\([^/]*\)/\(.*\)$@\1@')
    file=$(echo $filename|sed -e 's@licenses/\([^/]*\)/\(.*\)$@\2@')
    echo "Processing $package -> $file"
    id=$(echo "${package}_${file}" | tr -c -d '[0-9a-zA-Z-_]')
    (
        if [ ! -s "about/$package.html" ] ; then
            echo "<h3>$package</h3>"
        fi
        echo "<button uk-toggle=\"target: #${id}\" type=\"button\">${file}</button>"
        echo "<pre id=\"${id}\" hidden>"
        cat "$filename"
        echo "</pre>"
    ) >> "about/$package.html"
done

rm -f about/about.html
find about -type f | while read filename ; do
    cat "$filename" >> about/about.html
done
popd

mv output/planticam/legal-info/about/about.html package/planticam_web/static/