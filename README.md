<div align = "center" >
    <h1>pmccc</h1>

python minecraft launcher library

---

[
en_us
|
[zh_cn](./README-zh_cn.md)
]

</div>

---

``` python
import pmccc

main = pmccc.main( "./.minecraft" , "Demo" , "0.1" )
player = pmccc.player( "Dev" )
# main.use_url = "mcbbs"

version = "1.20.1"
# version = "1.12.2"
# version = "rd-132211"

main.install_version( version , version )

main.run( player , version )

```
