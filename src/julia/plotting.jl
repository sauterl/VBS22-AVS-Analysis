using CSV, DataFrames, CairoMakie, CategoricalArrays;

subs = DataFrame(CSV.File("../../data/avssubmissions.csv"));

# teams = unique(sort(subs.team)); # experimenting
# taskTeams = groupby(subs, [:task, :team]); # experimenting

# groupb by task and team, count (nrow) and get the unique values on task and team
submissionsPerTaskTeam = unique(combine(groupby(subs, [:task, :team]), :, nrow), [:task, :team]);

# sum up to get the total of submissions per task (again)
totals = combine(groupby(submissionsPerTaskTeam, [:task]), :nrow .=> sum => :sum);

# join on the task (name)
df = innerjoin(submissionsPerTaskTeam, totals, on = :task);

# calculate ratio
df[!,:ratio] = df[!,:nrow] ./ df[!,:sum];

# for plotting, convert to categorical
df[!,:task] = categorical(df[!,:task])
# for plotting, convert to categorical
df[!,:team] = categorical(df[!,:team])

# Makie barplot
p = barplot(
      df.task.refs, # the X avlues, must be numerical, hence the refs. multiple equal X values result in stacks
      df.ratio, # the Y values, must be numerical
      stack=df.team.refs, # numerical value of stack ordering
      color=df.team.refs, # numerical colour value within the theme (we use the same values as for the stacking)
      axis=( # customised axis
        xticks=( # x ticks
          1:length(levels(df.task)), # numerical version of xticks, basically indices for label (next argument)
          replace.(levels(df.task), "vbs22-avs-" => "a") # label. replacing "vbs22-avs-" in each label with "a", consistent with VBS'21 paper
        ), 
        title="Shares of submissions per team and task"
      ),
      bar_labels=df.team # apparently, categorical array works here, basically all the labels for all the bars (remember, they get stacked)
      );
      
save("../../plots/avs-team-ratios-total.pdf", p);