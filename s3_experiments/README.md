## Setting up S3 access

The main goal of these experiments were to tinker with all aspects of S3 manipulation and listing them below.

### Use Case 1:

Propagating data between steps and quickly switching between local and remote access for debugging. This is supposedly more space optimal.

In `s3_artifact_propagate.py`, we can switch between a local folder and S3 by doing the following for a remote run

`python s3_read_write.py  --datastore s3 --datastore-root s3://ish-metaflow-hackday run`

Or, the following for a local run

`python s3_read_write.py  --datastore local --datastore-root s3://ish-metaflow-hackday run`

This will create a S3 directory locally to run your artifacts again

To not specify the S3 directory each time, run `metaflow configure aws` where you can set defaults for tasks like S3, Batch and Step Functions

Now, you may simply run it as

`python s3_read_write.py  --datastore <your-mode> run`

### Use Case 2:

Workflows become more optimal with S3 involved when we exploit parallelism and other operations. Another advantage of this flow is that we can control the exact locations of stores and writes whereas
in the previous flow, it would be forcefully written to a path `s3://ish-metaflow-hackday/LinearFlow` with metadata and data subdirectories. The throughput and operations supported is also much higher in the current case.

In `s3_robust_operations.py`, we document single, multiple and parallel reads and writes. This runs entirely on AWS.

Run the script as`python s3_robust_operations.py run`