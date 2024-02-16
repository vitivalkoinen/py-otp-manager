import binascii
import json
import os
import uuid

import pyotp
from cryptography.fernet import Fernet


class OTPManager:
    def __init__(self):
        # ユーザーディレクトリ配下のパスを設定
        self.otp_dir = os.path.join(os.path.expanduser("~"), ".pyotp")
        if not os.path.exists(self.otp_dir):
            os.makedirs(self.otp_dir)
        self.otp_file = os.path.join(self.otp_dir, "otp_data")

        # 暗号化キーを生成または読み込み
        self.key_file = os.path.join(self.otp_dir, "key")
        if not os.path.exists(self.key_file):
            self.key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(self.key)
        else:
            with open(self.key_file, "rb") as f:
                self.key = f.read()
        self.cipher_suite = Fernet(self.key)

    def add_otp(self, service_name, secret_key):
        service_id = str(uuid.uuid4())
        data = f"{service_name},{secret_key},{service_id}"
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        with open(self.otp_file, "ab") as f:
            f.write(encrypted_data + b"\n")
        print(f"Added OTP for service: {service_name} with ID: {service_id}")

    def list_otps(self, output_format="table", search=None):
        if not os.path.exists(self.otp_file):
            print("No OTPs saved.")
            return
        otps = []
        with open(self.otp_file, "rb") as f:
            for line in f:
                decrypted_data = (
                    self.cipher_suite.decrypt(line.strip()).decode().strip()
                )
                service_name, _, service_id = decrypted_data.split(",", 2)
                if search is None or search.lower() in service_name.lower():
                    otps.append(
                        {"service_name": service_name, "service_id": service_id},
                    )

        if output_format == "json":
            print(json.dumps(otps, indent=2))
        else:
            print(f"{'Service Name':<20} | {'Service ID'}")
            print("-" * 40)
            for otp in otps:
                print(f"{otp['service_name']:<20} | {otp['service_id']}")

    def show_otp(self, service_id):
        found = False
        with open(self.otp_file, "rb") as f:
            for line in f:
                decrypted_data = (
                    self.cipher_suite.decrypt(line.strip()).decode().strip()
                )
                saved_service_name, secret_key, saved_service_id = decrypted_data.split(
                    ",",
                    2,
                )
                if saved_service_id == service_id:
                    found = True
                    try:
                        otp = pyotp.TOTP(secret_key).now()
                        print(
                            f"Current OTP for service {saved_service_name} with ID {service_id}: {otp}",  # noqa: E501
                        )
                    except binascii.Error:
                        print("秘密鍵が正しいBase32形式ではありません。")
                    break
        if not found:
            print("Service not found.")

    def rm_otp(self, service_id):
        found = False
        if not os.path.exists(self.otp_file):
            print("No OTPs saved.")
            return
        with open(self.otp_file, "rb") as f:
            lines = f.readlines()
        with open(self.otp_file, "wb") as f:
            for line in lines:
                decrypted_data = (
                    self.cipher_suite.decrypt(line.strip()).decode().strip()
                )
                _, _, saved_service_id = decrypted_data.split(",", 2)
                if saved_service_id != service_id:
                    f.write(line)
                else:
                    found = True
                    print(f"Deleted OTP with ID: {service_id}")
        if not found:
            print("Service not found.")
