import argparse

from otp_manager.otp_manager import OTPManager


def main():
    parser = argparse.ArgumentParser(description="CLIベースでOTPを管理")
    parser.add_argument(
        "action", choices=["add", "rm", "show", "list"], help="実行するアクション",
    )
    parser.add_argument("--service", type=str, help="サービス名")
    parser.add_argument("--key", type=str, help="シークレットキー")
    parser.add_argument("--id", type=str, help="ID")
    parser.add_argument(
        "--output",
        type=str,
        choices=["json", "table"],
        default="table",
        help="出力形式",
    )
    parser.add_argument("--search", type=str, help="検索キーワード")

    args = parser.parse_args()
    otp_manager = OTPManager()

    if args.action == "list":
        otp_manager.list_otps(args.output, args.search)
    elif args.action == "add" and args.service and args.key:
        otp_manager.add_otp(args.service, args.key)
    elif args.action == "rm" and args.id:
        otp_manager.rm_otp(args.id)
    elif args.action == "show" and args.id:
        otp_manager.show_otp(args.id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
