using CSV, DataFrames, CairoMakie, CategoricalArrays
using ColorSchemes, ColorBrewer

juds = DataFrame(CSV.File("../../data/avs-submissions-judgements.csv"));
# Time between submission and prepare (a judge requested the submission)
juds.deltaPrep = (juds.ptimestamp - juds.stimestamp) ./ 1000; #ms
# Time between prepare and judgement (the time it took the judge)
juds.deltaJudge = (juds.jtimestamp - juds.ptimestamp) ./ 1000;
# Total time it took between submission and verdict
juds.deltaAll = (juds.jtimestamp - juds.stimestamp) ./ 1000;

# categorise it
juds.stask = categorical(juds.stask);

fig = Figure();
labels = replace.(levels(juds.stask), "vbs22-avs-" => "a"); # label. replacing "vbs22-avs-" in each label with "a", consistent with VBS'21 paper
ax = Axis(fig[1,1],
          xticks = ( # x ticks
          1:length(levels(juds.stask)), # numerical version of xticks, basically indices for label (next argument)
          labels),
        title="Time judges took to for their verdict",
        xlabel = "tasks",
        ylabel = "seconds"
     );

boxplot!(ax, juds.stask.refs, juds.deltaJudge);

save("../../plots/avs-judgement-time.pdf", fig);
