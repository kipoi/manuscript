import argparse
import time
import kipoi
from kipoi.data_utils import numpy_collate
from kipoi.utils import parse_json_file_str
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="kipoi model")
    parser.add_argument("--model_group", help="kipoi model")
    parser.add_argument("--dl_kwargs", help="Dataloader kwargs")
    parser.add_argument("--batch_size", required=True, type=int, help="Batch size to run")
    parser.add_argument("--num_runs", required=True, type=int, help="Number of runs to perform")
    parser.add_argument("--num_workers", required=True, type=int, help="Number of workers used to load the data")
    parser.add_argument("--tf", required=True, help="Transcription factor to benchmark")
    parser.add_argument("--output", "-o", required=True, help="Transcription factor to benchmark")
    args = parser.parse_args()

    model = kipoi.get_model(args.model)

    print("Obtaining a batch of data, using {} workers".format(args.num_workers))
    dl_kwargs = kipoi.pipeline.validate_kwargs(model.default_dataloader, parse_json_file_str(args.dl_kwargs))
    print("Used kwargs: {}".format(dl_kwargs))
    dl = model.default_dataloader(**dl_kwargs)
    # batch = numpy_collate([dl[0]]*args.batch_size)
    it = dl.batch_iter(args.batch_size, num_workers=args.num_workers)
    batch = next(it)

    print("Measuring the forward time pass")
    times = []
    for i in range(args.num_runs):
        start_time = time.time()
        model.predict_on_batch(batch['inputs'])
        duration = time.time() - start_time
        times.append(duration)

    print("Writing results to a json file")
    result = {"times": times,
              "model": args.model,
              "model_group": args.model_group,
              "num_runs": args.num_runs,
              "tf": args.tf}
    with open(args.output, "w") as f:
        json.dump(result, f)

    print("Done!")
