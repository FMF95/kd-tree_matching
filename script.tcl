clear

# Seleccionar nodos para las dos listas
*createmarkpanel nodes 1 "Select nodes for the list a:"
set node_list_a [ hm_getmark nodes 1 ];
*createmarkpanel nodes 1 "Select nodes for the list b:"
set node_list_b [ hm_getmark nodes 1 ];

# Obtener el directorio del script actual
set ScriptDir [file dirname [file normalize [info script]]]

#puts "list A: $node_list_a"
#puts "list B: $node_list_b"

set list_names "node_list_a node_list_b"

# Exportar las listas de nodos a archivos CSV
foreach list $list_names {
    eval set eval_list $$list
    #puts "$list: $eval_list"
    
    set path "[file join $ScriptDir "$list.csv"]"
    #puts $path
    set outfile [open $path w]
    puts $outfile "ID,x,y,z"
    
    foreach node $eval_list {
        set node_x [hm_getvalue nodes id=$node dataname=x]
        set node_y [hm_getvalue nodes id=$node dataname=y]
        set node_z [hm_getvalue nodes id=$node dataname=z]
    
    puts $outfile "$node,$node_x,$node_y,$node_z"

    }
    
    close $outfile
}

# Ejecutar el script de Python
set pypath "[file join $ScriptDir "matching.py"]"
set pycpath "[file join $ScriptDir "matching.cpython-311.pyc"]"
set list_a_path "[file join $ScriptDir "node_list_a.csv"]"
set list_b_path "[file join $ScriptDir "node_list_b.csv"]"
set output_path "[file join $ScriptDir "matching.csv"]"

# Verificar si el archivo .py o .pyc existe
if {[catch {file exists $pypath} exists1] || !$exists1} {

    if {[catch {file exists $pycpath} exists2] || !$exists2} {
        error "No se encontró ninguno de los archivos:\n$pypath\n$pycpath"
    } else {
        set matchpath $pycpath
    }

} else {
    set matchpath $pypath
}
#puts "Usando archivo: $matchpath"

# Construir el comando
set command ""
append command "python" " " "\"$matchpath\"" " " "\"$list_a_path\"" " " "\"$list_b_path\"" " " "--output" " " "\"$output_path\""

# Ejecutar el comando
#puts $command
eval exec $command

# Abrir el archivo
set outfile [open $output_path r]

# Listas para cada columna
set ID_A {}
set ID_B {}
set Distance {}

# Leer y descartar encabezado
gets $outfile

# Leer línea a línea
while {[gets $outfile line] >= 0} {

    # Separar por comas
    set fields [split $line ","]

    # Asignar cada columna
    lappend ID_A [lindex $fields 0]
    lappend ID_B [lindex $fields 1]
    lappend Distance [lindex $fields 2]
}

# Cerrar archivo
close $outfile

# Crear componente para visualizar las distancias
if { ![catch { *createentity comps includeid=0 name=^distance_marks }] } {
	*currentcollector components "^distance_marks"
}
*createmark elems 1 "by collector name" "^distance_marks"
if { [hm_marklength elems 1] > 0 } { *deletemark elems 1 }
*clearmark elems 1
*createmark components 1 "^distance_marks"
*setvalue comps mark=1 color=6
*clearmark components 1
*createmark tags 1 "by name" ^Measure:

# Crear líneas entre los nodos emparejados
*tagtextdisplaymode 3
foreach id_a $ID_A id_b $ID_B distance $Distance {
    puts "ID_A: $id_a, ID_B: $id_b, Distance: $distance"
    *createlist nodes 1 $id_a $id_b
    *createelement 2 1 1 1
    set plotid [hm_latestentityid elems]
    #*createmark elems 1 1
    #*tagcreate elems 1 "tag_text"
    #*setvalue tags id=5 color=6
}

return