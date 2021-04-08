from metaflow import FlowSpec, step, S3
import json


class S3DemoFlow(FlowSpec):
    @step
    def start(self):
        with S3(run=self, s3root="s3://ish-metaflow-hackday") as s3:
            print("Singular scoped puts")
            message = json.dumps({"message": "hello world!"})
            s3.put("sample_obj_1", message)
            s3.put("sample_obj_2", message)
        self.next(self.singular_access)

    @step
    def singular_access(self):
        with S3(run=self, s3root="s3://ish-metaflow-hackday") as s3:
            print("Singular scoped gets")
            s3obj_1 = s3.get("sample_obj_1")
            print("Object found at", s3obj_1.url)
            print("Message:", json.loads(s3obj_1.text))
            s3obj_2 = s3.get("sample_obj_2")
            print("Object found at", s3obj_2.url)
            print("Message:", json.loads(s3obj_2.text))
        self.next(self.multiple_access)

    @step
    def multiple_access(self):
        print("Multiple object access")
        many = {"first_key": "foo", "second_key": "bar"}
        with S3(s3root="s3://ish-metaflow-hackday") as s3:
            s3.put_many(many.items())
            objs = s3.get_many(["first_key", "second_key"])
            print(objs)
        self.next(self.recursive_listing)

    @step
    def recursive_listing(self):
        with S3(run=self, s3root="s3://ish-metaflow-hackday") as s3:
            objs = s3.get_all()
            print(objs)
        self.next(self.end)

    @step
    def end(self):
        pass


if __name__ == "__main__":
    S3DemoFlow()
