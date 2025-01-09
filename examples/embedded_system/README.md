# Embedded System Example

This example shows what might be possible if generating C++ code for an embedded system that has a JSON configuration file.

```bash
python examples/embedded_system/gen.py -v debug -o generated examples/embedded_system/config.json
cat << EOF > main.cpp
#include <iostream>
#include "Config.h"

int main()
{
    std::cout << Config::hello << " " << Config::world << std::endl;
    return 0;
}
EOF
g++ -o hello main.cpp Config.cpp
```

> [!TIP]
> Modify `examples/embedded_system/config.json` to use `german.properties` so `hello` outputs in German.
> Feel free to add more languages to test it out.
