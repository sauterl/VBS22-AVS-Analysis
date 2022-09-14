using JSON3, CSV, DataFrames, JSONTables;

runJson = JSON3.read(read("../../data/run_vbs_2022.json", String));

# Submissions contain team IDs
teamIdMap = Dict(map(e -> e[:uid][:string] => e[:name], runJson[:description][:teams]));

avsTasks = filter(e ->  e[:description][:taskGroup][:name]=="VBS2022-AVS", runJson[:tasks]);
unusedTasks = filter(e -> length(e[:submissions]) <= 0, avsTasks);
tasks = filter(e -> length(e[:submissions]) > 0 , avsTasks);

submissionsDF = DataFrame[];
tasksDF = DataFrame[];

for t in tasks
  taskName = t[:description][:name];
  taskGroup = t[:description][:taskGroup][:name]; # Should only be "VBS2022-AVS"
  taskHint = t[:description][:hints][1][:text]; # We know, since its AVS that there is only one hint
  taskDuration = t[:description][:duration];
  
  push!(tasksDF, DataFrame(
    uid = t[:uid][:string],
    name = taskName,
    group = taskGroup,
    duration = taskDuration,
    hint = taskHint,
    started = t[:started],
    ended = t[:ended]
  ));
  
  for s in t[:submissions]
    push!(submissionsDF, DataFrame(
      uid = s[:uid][:string],
      taskId = t[:uid][:string];
      task = taskName,
      group = taskGroup,
      time = s[:timestamp] - t[:started] + 5000,
      team = teamIdMap[s[:teamId][:string]],
      member = s[:memberId][:string],
      item = s[:item][:name],
      start = s[:start],
      ending = s[:end],
      status = s[:status]
    ));
  end
end

CSV.write("avssubmissions.csv", vcat(submissionsDF...));
CSV.write("avstasks.csv",vcat(tasksDF...));