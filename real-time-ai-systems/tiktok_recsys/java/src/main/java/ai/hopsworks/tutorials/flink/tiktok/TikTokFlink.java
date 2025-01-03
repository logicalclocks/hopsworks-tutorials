package ai.hopsworks.tutorials.flink.tiktok;

import ai.hopsworks.tutorials.flink.tiktok.pipelines.TikTokStreamFeatureAggregations;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;

public class TikTokFlink {
    public static void main(String[] args) throws Exception {

        Options options = new Options();

        options.addOption(Option.builder("maxIdRange")
                .argName("maxIdRange")
                .required(false)
                .hasArg()
                .build());

        options.addOption(Option.builder("recordsPerSecond")
                .argName("recordsPerSecond")
                .required(false)
                .hasArg()
                .build());

        options.addOption(Option.builder("parallelism")
                .argName("parallelism")
                .required(false)
                .hasArg()
                .build());

        CommandLineParser parser = new DefaultParser();
        CommandLine commandLine = parser.parse(options, args);

        Long maxId = 100000000L;
        if (commandLine.hasOption("maxIdRange")) {
            maxId =  Long.parseLong(commandLine.getOptionValue("maxIdRange"));
        }

        Long recordsPerSecond = 1000000L;
        if (commandLine.hasOption("recordsPerSecond")) {
            recordsPerSecond =  Long.parseLong(commandLine.getOptionValue("recordsPerSecond"));
        }

        Integer parallelism = 200;
        if (commandLine.hasOption("parallelism")) {
            parallelism = Integer.parseInt(commandLine.getOptionValue("parallelism"));
        }

        new TikTokStreamFeatureAggregations().stream(maxId, recordsPerSecond, parallelism);
    }
}
