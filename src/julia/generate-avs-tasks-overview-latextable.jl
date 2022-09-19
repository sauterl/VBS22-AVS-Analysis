using JSON3, CSV, DataFrames, JSONTables, Latexify;

tasks = DataFrame(CSV.File("../../data/avs-tasks.csv"));

# beautify and consistently change labels
tasks.name = replace.(tasks.name, "vbs22-avs-" => "a");

# sanitise hints
tasks.hint = replace.(tasks.hint, "\n" => "");
tasks.hint = replace.(tasks.hint, "\t" => "");
tasks.hint = rstrip.(tasks.hint);

#create LaTeX
tex = latexify(tasks[:,[:name,:hint]]);