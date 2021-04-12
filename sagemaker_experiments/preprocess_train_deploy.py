import gzip
import io
import os
import pickle

import boto3
import numpy as np
import sagemaker.amazon.common as smac
from metaflow import S3, FlowSpec, Parameter, step, batch
from sagemaker import get_execution_role
from sagemaker.estimator import Estimator


class SagemakerTrainDeployFlow(FlowSpec):
    """
    A flow for Metaflow to demonstrate Sagemaker training and deployment
    """

    DOCKER_IMAGE_URI = Parameter(
        name="sagemaker_image",
        help="AWS Docker Image URI for SageMaker Inference",
        default="382416733822.dkr.ecr.us-east-1.amazonaws.com/linear-learner:latest",
    )
    SAGEMAKER_INSTANCE = Parameter(
        name="sagemaker_instance",
        help="AWS Instance to Power SageMaker Inference",
        default="ml.t2.medium",
    )
    SAGEMAKER_ROLE = Parameter(
        name="sagemaker_role",
        help="Sagemaker role to use",
        default="arn:aws:iam::545978490421:role/service-role/AmazonSageMaker-ExecutionRole-20190813T105533",
    )
    HACKDAY_BUCKET = "s3://ish-metaflow-hackday"

    @step
    def start(self):
        self.next(self.preprocess)
    
    @batch(cpu=1, memory=20000)
    @step
    def preprocess(self):
        s3 = boto3.resource("s3")
        s3.Object("ish-metaflow-hackday", "mnist.pkl.gz").download_file("mnist.pkl.gz")

        with gzip.open("mnist.pkl.gz") as f:
            pickled_data = f.read()
        train_set, _, _ = pickle.loads(pickled_data, encoding="latin1")
        train_vectors = np.array([t.tolist() for t in train_set[0]]).astype("float32")
        train_vectors = np.repeat(train_vectors, 40, 0)
        train_labels = np.where(
            np.array([t.tolist() for t in train_set[1]]) == 0, 1, 0
        ).astype("float32")
        train_labels = np.repeat(train_labels, 40, 0)
        buf = io.BytesIO()
        smac.write_numpy_to_dense_tensor(buf, train_vectors, train_labels)
        buf.seek(0)

        with S3(run=self, s3root=self.HACKDAY_BUCKET) as s3:
            self.location = s3.put("training_data", buf.read())

        self.next(self.train)

    @step
    def train(self):
        """
        Train and deploy the XOR model with Sagemaker Linear Learner
        """
        estimator = Estimator(
            image_uri=self.DOCKER_IMAGE_URI,
            role=self.SAGEMAKER_ROLE,
            instance_count=1,
            hyperparameters={"predictor_type": "binary_classifier"},
            instance_type="ml.m5.large",
        )
        estimator.fit({"train": self.location})
        estimator.deploy(
            initial_instance_count=1, instance_type=self.SAGEMAKER_INSTANCE, wait=False
        )
        self.next(self.end)

    @step
    def end(self):
        pass


if __name__ == "__main__":
    SagemakerTrainDeployFlow()
