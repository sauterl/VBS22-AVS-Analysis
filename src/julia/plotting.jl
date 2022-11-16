using CSV, DataFrames, CairoMakie, CategoricalArrays;
using ColorSchemes, ColorBrewer;

subs = DataFrame(CSV.File("../../data/avs-submissions.csv"));
csubs = filter(:status => s -> s == "CORRECT", subs);

# groupb by task and team, count (nrow) and get the unique values on task and team
submissionsPerTaskTeam = unique(combine(groupby(subs, [:task, :team]), :, nrow), [:task, :team]);
csubPerTT = unique(combine(groupby(csubs, [:task, :team]), :, nrow), [:task, :team]);

# sum up to get the total of submissions per task (again)
totals = combine(groupby(submissionsPerTaskTeam, [:task]), :nrow .=> sum => :sum);
ctotals = combine(groupby(csubPerTT, [:task]), :nrow .=> sum => :sum);

# join on the task (name)
df = innerjoin(submissionsPerTaskTeam, totals, on = :task);
cdf = innerjoin(csubPerTT, ctotals, on = :task);

# calculate ratio
df[!,:ratio] = df[!,:nrow] ./ df[!,:sum];
cdf.ratio = cdf.nrow ./ cdf.sum;

# for plotting, convert to categorical
df[!,:task] = categorical(df[!,:task]);
cdf.task = categorical(cdf.task);
# for plotting, convert to categorical
df[!,:team] = categorical(df[!,:team]);
cdf.team = categorical(cdf.team);



fig = Figure();
cfig = Figure();
labels = replace.(levels(df.task), "vbs22-avs-" => "a"); # label. replacing "vbs22-avs-" in each label with "a", consistent with VBS'21 paper
teams = levels(df.team);
colors= get(ColorSchemes.cork, collect(0:1/(length(teams)-1):1)); # sampling color scheme. values must be between 0 and 1, hence the division
ax = Axis(fig[1,1],
          xticks = ( # x ticks
          1:length(levels(df.task)), # numerical version of xticks, basically indices for label (next argument)
          labels),
        title="Shares of submissions per team and task"
     );
cax = Axis(cfig[1,1],
          xticks = ( # x ticks
          1:length(levels(cdf.task)), # numerical version of xticks, basically indices for label (next argument)
          labels),
        title="Shares of correct submissions per team and task"
     );


# Makie barplot
barplot!(ax,
      df.task.refs, # the X avlues, must be numerical, hence the refs. multiple equal X values result in stacks
      df.ratio, # the Y values, must be numerical
      stack=df.team.refs, # numerical value of stack ordering
      color=colors[df.team.refs], # numerical colour value within the theme (we use the same values as for the stacking)
      # bar_labels=df.team # apparently, categorical array works here, basically all the labels for all the bars (remember, they get stacked)
      );
      
barplot!(cax,
      cdf.task.refs, # the X avlues, must be numerical, hence the refs. multiple equal X values result in stacks
      cdf.ratio, # the Y values, must be numerical
      stack=cdf.team.refs, # numerical value of stack ordering
      color=colors[cdf.team.refs], # numerical colour value within the theme (we use the same values as for the stacking)
      );

elements = [PolyElement(markercolor = i, linecolor=i,polycolor=i) for i in colors[1:length(teams)]]; # same sampling as for color def.
Legend(fig[1,2], reverse(elements), reverse(teams), "Teams");
Legend(cfig[1,2], reverse(elements), reverse(teams), "Teams");
      
save("../../plots/avs-team-ratios-total.pdf", fig);
save("../../plots/avs-team-ratios-correct.pdf", cfig);