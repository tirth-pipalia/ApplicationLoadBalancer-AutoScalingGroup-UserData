from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    aws_ec2 as ec2,
    aws_autoscaling as auto_scaling,
    aws_elasticloadbalancingv2 as elbv2,
)
from constructs import Construct


class AutoScalingStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs, tags={"cost-center": "8998",
                                                              "department": "Information-technology",
                                                              "workload-name": "rms-webserver-prod"})

        VPC = ec2.Vpc.from_lookup(
            self,
            "VPCid",
            vpc_name="rms-prod-vpc",
        )

        elasticLoadBalancer = elbv2.ApplicationLoadBalancer(
            self,
            'LoadBalancerId',
            vpc=VPC,
            internet_facing=True,
            load_balancer_name='rms-loadbalance-prod',
        )
        listner = elasticLoadBalancer.add_listener(
            'ELB-listner-id',
            open=True,
            port=80,
        )

        userData = ec2.UserData.for_linux()
        userData.add_commands(
            "#!/bin/bash",
            "yum update-y",
            "yum install httpd -y",
            "service httpd start",
            "chkconfig httpd on",
            "cd /var/www/html",
            "echo \"<html><h1>This is DevOPS Session</h1></html>\" > index.html"
        )
        instanceInput = self.node.try_get_context("instanceInput")

        autoScaling = auto_scaling.AutoScalingGroup(
            self,
            "ASGid",
            instance_type=ec2.InstanceType.of(ec2.InstanceClass[instanceInput["instanceClass"]],
                                              ec2.InstanceSize[instanceInput["instanceSize"]]),
            machine_image=ec2.AmazonLinuxImage(),
            vpc=VPC,
            user_data=userData,
            auto_scaling_group_name='rms-autoSlcalinGroup-prod',
            desired_capacity=2,
            key_name='TirthBahrain-KP',
            max_capacity=2,
            min_capacity=2,
            vpc_subnets=ec2.SubnetSelection(availability_zones=['me-south-1a', 'me-south-1b'],
                                            subnet_type=ec2.SubnetType.PUBLIC)
        )

        listner.add_targets('default-target',
                            port=80,
                            targets=[autoScaling],
                            health_check=elbv2.HealthCheck(
                                enabled=True,
                                path='/index.html',
                                unhealthy_threshold_count=2,
                                healthy_threshold_count=2,
                                timeout=Duration.seconds(10)
                            )
                            )

        # listner.add_action('/static',
        #                    priority=5,
        #                    conditions=[elbv2.ListenerCondition.path_patterns(['/static'])],
        #                    action=elbv2.ListenerAction.fixed_response(200,content_type='text/html',
        #                                                               message_body='<h1> Static ALB Response')
        #                    )

        autoScaling.scale_on_request_count('request-per-minuse',
                                           target_requests_per_minute=2,
                                           )

        # autoScaling.scale_on_cpu_utilization('scaleOnCPUUtlization',
        #                                      target_utilization_percent=2)

        CfnOutput(self, 'ALBDNS',
                  value=elasticLoadBalancer.load_balancer_dns_name)
