import sys
import argparse
import logging
from rich.logging import RichHandler
import yaml

from gaarf.io import writer, reader  # type: ignore
from gaarf.simulation import simulate_data, SimulatorSpecification
from .utils import GaarfConfigBuilder, init_logging


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="+")
    parser.add_argument("-c", "--config", dest="gaarf_config", default=None)
    parser.add_argument("-s",
                        "--simulator-config",
                        dest="simulator_config",
                        default=None)
    parser.add_argument("--account", dest="customer_id", default="None")
    parser.add_argument("--output", dest="save", default="console")
    parser.add_argument("--input", dest="input", default="file")
    parser.add_argument("--api-version", dest="api_version", default=13)
    parser.add_argument("--log", "--loglevel", dest="loglevel", default="info")
    parser.add_argument("--logger", dest="logger", default="local")
    parser.add_argument("--customer-ids-query",
                        dest="customer_ids_query",
                        default=None)
    parser.add_argument("--customer-ids-query-file",
                        dest="customer_ids_query_file",
                        default=None)
    parser.add_argument("--save-config",
                        dest="save_config",
                        action="store_true")
    parser.add_argument("--no-save-config",
                        dest="save_config",
                        action="store_false")
    parser.add_argument("--config-destination",
                        dest="save_config_dest",
                        default="config.yaml")
    parser.set_defaults(save_config=False)
    args = parser.parse_known_args()
    main_args = args[0]

    logger = init_logging(loglevel=main_args.loglevel.upper(),
                          logger_type=main_args.logger)

    config = GaarfConfigBuilder(args).build()
    logger.debug("config: %s", config)

    writer_client = writer.WriterFactory().create_writer(
        config.output, **config.writer_params)
    if config.output == "bq":
        _ = writer_client.create_or_get_dataset()
    reader_factory = reader.ReaderFactory()
    reader_client = reader_factory.create_reader(main_args.input)

    for query in main_args.query:
        if simulator_config := main_args.simulator_config:
            with open(simulator_config, encoding="utf-8") as f:
                simulator_config = yaml.safe_load(f)
            simulator_specification = SimulatorSpecification(
                **simulator_config)
        else:
            simulator_specification = SimulatorSpecification()
        logger.info("Simulating data for query %s", query)
        report = simulate_data(reader_client.read(query),
                               simulator_specification)
        writer_client.write(report, query)


if __name__ == "__main__":
    main()
