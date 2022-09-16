using CSV, DataFrames, CairoMakie, CategoricalArrays;

subs = DataFrame(CSV.File("../../data/avssubmissions.csv"));

teams = unique(sort(subs.team));

taskTeams = groupby(subs, [:task, :team]);

submissionsPerTaskTeam = unique(combine(groupby(subs, [:task, :team]), :, nrow), [:task, :team]);

totals = combine(groupby(submissionsPerTaskTeam, [:task]), :nrow .=> sum => :sum);

df = innerjoin(submissionsPerTaskTeam, totals, on = :task);

df[!,:ratio] = df[!,:nrow] ./ df[!,:sum];
df[!,:task] = categorical(df[!,:task])
df[!,:team] = categorical(df[!,:team])

p = barplot(df.task.refs, df.ratio,stack=df.team.refs,color=df.team.refs,axis=(xticks=(1:length(levels(df.task)), levels(df.task)), title="Shares of submissions per team and task"),bar_labels=df.team);
save("../../plots/avs-team-ratios-total.pdf", p);