#!/usr/bin/env python3
"""Bitbull Capital inter-agent messaging.

Messages are files in a workspace both parties belong to. Two roles may only
exchange messages if they share a workspace — which is how the hierarchy is
enforced: there is no channel from the CEO to the trader, because they share
no room.

    scripts/msg.py new  --from cfo --to market-analyst --type work-order \
        --re "Momentum mandate" --body-file brief.md
    scripts/msg.py inbox --role market-analyst
    scripts/msg.py show  <message-id>
    scripts/msg.py reply --from market-analyst --to cfo --in-reply-to <id> \
        --type report --body-file proposal.md
    scripts/msg.py close <message-id>
    scripts/msg.py routes --role cfo
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "workspaces" / "registry.json"


def load():
    with REGISTRY.open() as fh:
        return json.load(fh)


def die(msg):
    print(f"REFUSED: {msg}", file=sys.stderr)
    raise SystemExit(2)


def slug(text, limit=48):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (s[:limit].rstrip("-")) or "untitled"


def shared_workspaces(reg, a, b):
    for role in (a, b):
        if role not in reg["roles"]:
            die(f"unknown role '{role}'. Known roles: {', '.join(sorted(reg['roles']))}")
    return [w for w in reg["roles"][a]["workspaces"] if w in reg["roles"][b]["workspaces"]]


def chain_up(reg, role):
    """Role and each manager above it, up to the founder."""
    chain, seen = [role], {role}
    while role in reg["roles"]:
        role = reg["roles"][role].get("reports_to")
        if not role or role in seen:
            break
        chain.append(role)
        seen.add(role)
    return chain


def neighbours(reg, role):
    """Roles this role shares a workspace with — the channels it actually has."""
    out = set()
    for name in reg["roles"][role]["workspaces"]:
        out.update(reg["workspaces"][name]["members"])
    out.discard(role)
    return out


def hierarchy_route(reg, sender, to):
    """Shortest legitimate route: hop by hop through roles that share a workspace.

    Peers in the exec room are one hop apart, so finance->engineering goes
    cfo -> cto rather than up through the CEO.
    """
    from collections import deque

    prev = {sender: None}
    queue = deque([sender])
    while queue:
        node = queue.popleft()
        if node == to:
            path = []
            while node is not None:
                path.append(node)
                node = prev[node]
            return list(reversed(path))
        for nxt in sorted(neighbours(reg, node)):
            if nxt not in prev:
                prev[nxt] = node
                queue.append(nxt)
    # Disconnected (e.g. the founder, who is not a workspace member): fall back
    # to the reporting chain.
    up_sender, up_to = chain_up(reg, sender), chain_up(reg, to)
    for i, node in enumerate(up_sender):
        if node in up_to:
            j = up_to.index(node)
            return up_sender[: i + 1] + list(reversed(up_to[:j]))
    return [sender, to]


def pick_workspace(reg, sender, to, requested, msg_type):
    shared = shared_workspaces(reg, sender, to)
    broadcast = msg_type in reg["broadcast_types"]
    if requested:
        if requested not in reg["workspaces"]:
            die(f"unknown workspace '{requested}'")
        if requested not in shared and not broadcast:
            die(
                f"'{sender}' and '{to}' do not share workspace '{requested}'. "
                f"Shared: {shared or 'none'}"
            )
        return requested
    if shared:
        return shared[0]
    if broadcast:
        # The one exception to the wall: a halt notice goes where the recipient
        # will actually see it, even if that is not the sender's room.
        theirs = reg["roles"][to]["workspaces"]
        return theirs[0] if theirs else reg["roles"][sender]["workspaces"][0]
    route = " -> ".join(hierarchy_route(reg, sender, to))
    die(
        f"'{sender}' has no channel to '{to}' — they share no workspace.\n"
        f"         Route it through the chain of command: {route}\n"
        f"         (Cross-team artifacts are published to specs/ by a bridging executive.\n"
        f"          A halt-notice is the only message type that may bypass this.)"
    )


def message_path(reg, workspace, message_id):
    return ROOT / reg["workspaces"][workspace]["path"] / "messages" / f"{message_id}.md"


def read_body(args):
    if args.body_file == "-":
        return sys.stdin.read().rstrip() + "\n"
    if args.body_file:
        p = pathlib.Path(args.body_file)
        if not p.exists():
            die(f"body file not found: {p}")
        return p.read_text().rstrip() + "\n"
    if args.body:
        return args.body.rstrip() + "\n"
    return "<!-- body -->\n"


def cmd_new(args, reg, in_reply_to=None):
    sender, to = args.sender, args.to
    if sender == to:
        die("a role cannot message itself")
    if args.type not in reg["message_types"]:
        die(f"unknown type '{args.type}'. Allowed: {', '.join(reg['message_types'])}")
    workspace = pick_workspace(reg, sender, to, args.workspace, args.type)

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    message_id = f"{stamp}-{sender}-to-{to}-{slug(args.re_)}"
    path = message_path(reg, workspace, message_id)
    if path.exists():
        die(f"message already exists: {path.relative_to(ROOT)}")
    path.parent.mkdir(parents=True, exist_ok=True)

    front = [
        "---",
        f"id: {message_id}",
        f"from: {sender}",
        f"to: {to}",
        f"workspace: {workspace}",
        f"type: {args.type}",
        f"re: {args.re_}",
        f"in_reply_to: {in_reply_to or 'null'}",
        "status: open",
        f"needs_by: {args.needs_by or 'null'}",
        f"created: {dt.datetime.now().isoformat(timespec='minutes')}",
        "---",
        "",
    ]
    path.write_text("\n".join(front) + read_body(args))
    print(f"{path.relative_to(ROOT)}")
    print(f"id: {message_id}  workspace: {workspace}")


def find_message(reg, message_id):
    for ws in reg["workspaces"].values():
        p = ROOT / ws["path"] / "messages" / f"{message_id}.md"
        if p.exists():
            return p
    die(f"no message with id '{message_id}'")


def parse_front(path):
    text = path.read_text()
    if not text.startswith("---"):
        return {}, text
    _, front, body = text.split("---", 2)
    meta = {}
    for line in front.strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, body.lstrip("\n")


def cmd_inbox(args, reg):
    role = args.role
    if role not in reg["roles"]:
        die(f"unknown role '{role}'")
    own = [
        name
        for name, ws in reg["workspaces"].items()
        if role in ws["members"] or role in ws.get("readers", [])
    ]
    rows = []
    for name, ws in reg["workspaces"].items():
        for p in sorted((ROOT / ws["path"] / "messages").glob("*.md")):
            meta, _ = parse_front(p)
            if meta.get("to") != role:
                continue
            # Rooms you are in, plus halt notices from anywhere — stopping is never gated.
            if name not in own and meta.get("type") not in reg["broadcast_types"]:
                continue
            if not args.all and meta.get("status") != "open":
                continue
            rows.append((name, meta, p))
    if not rows:
        print(f"inbox empty for {role}" + ("" if args.all else " (no open messages)"))
        return
    print(f"{len(rows)} message(s) for {role}:\n")
    for name, meta, p in rows:
        flag = "!" if meta.get("type") in reg["broadcast_types"] else " "
        print(f" {flag}[{name}] {meta.get('type','?'):<16} from {meta.get('from','?'):<18} "
              f"{meta.get('re','')}")
        print(f"      id: {meta.get('id')}  status: {meta.get('status')}  "
              f"needs_by: {meta.get('needs_by')}")


def cmd_show(args, reg):
    p = find_message(reg, args.id)
    print(p.read_text())


def cmd_reply(args, reg):
    parent = find_message(reg, args.in_reply_to)
    meta, _ = parse_front(parent)
    if meta.get("to") != args.sender:
        print(
            f"note: {args.sender} is replying to a message addressed to "
            f"{meta.get('to')} — check that this is intended.",
            file=sys.stderr,
        )
    if not args.re_:
        args.re_ = f"Re: {meta.get('re','(no subject)')}"
    cmd_new(args, reg, in_reply_to=args.in_reply_to)
    if meta.get("status") == "open":
        text = parent.read_text().replace("status: open", "status: answered", 1)
        parent.write_text(text)
        print(f"marked {args.in_reply_to} as answered")


def cmd_close(args, reg):
    p = find_message(reg, args.id)
    text = p.read_text()
    for old in ("status: open", "status: answered"):
        if old in text:
            p.write_text(text.replace(old, "status: closed", 1))
            print(f"closed {args.id}")
            return
    print(f"{args.id} is already closed")


def cmd_routes(args, reg):
    role = args.role
    if role not in reg["roles"]:
        die(f"unknown role '{role}'")
    info = reg["roles"][role]
    print(f"{role} ({info['title']}) reports to: {info['reports_to']}")
    print(f"workspaces: {', '.join(info['workspaces'])}\n")
    reachable = {}
    for ws in info["workspaces"]:
        for member in reg["workspaces"][ws]["members"]:
            if member != role:
                reachable.setdefault(member, []).append(ws)
    print("may message directly:")
    for member, rooms in sorted(reachable.items()):
        print(f"  {member:<20} via {', '.join(rooms)}")
    unreachable = [r for r in reg["roles"] if r != role and r not in reachable]
    if unreachable:
        print("\nno direct channel (route through the hierarchy):")
        for r in sorted(unreachable):
            print(f"  {r}")


def main():
    reg = load()
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_compose(p):
        p.add_argument("--from", dest="sender", required=True)
        p.add_argument("--to", required=True)
        p.add_argument("--type", required=True)
        p.add_argument("--re", dest="re_", default="")
        p.add_argument("--workspace")
        p.add_argument("--needs-by", dest="needs_by")
        p.add_argument("--body")
        p.add_argument("--body-file")

    p_new = sub.add_parser("new", help="send a message")
    add_compose(p_new)

    p_reply = sub.add_parser("reply", help="reply to a message")
    add_compose(p_reply)
    p_reply.add_argument("--in-reply-to", required=True)

    p_inbox = sub.add_parser("inbox", help="list messages addressed to a role")
    p_inbox.add_argument("--role", required=True)
    p_inbox.add_argument("--all", action="store_true", help="include answered and closed")

    p_show = sub.add_parser("show", help="print a message")
    p_show.add_argument("id")

    p_close = sub.add_parser("close", help="mark a message closed")
    p_close.add_argument("id")

    p_routes = sub.add_parser("routes", help="show who a role may talk to")
    p_routes.add_argument("--role", required=True)

    args = ap.parse_args()
    if args.cmd == "new":
        if not args.re_:
            die("--re is required")
        cmd_new(args, reg)
    elif args.cmd == "reply":
        cmd_reply(args, reg)
    elif args.cmd == "inbox":
        cmd_inbox(args, reg)
    elif args.cmd == "show":
        cmd_show(args, reg)
    elif args.cmd == "close":
        cmd_close(args, reg)
    elif args.cmd == "routes":
        cmd_routes(args, reg)


if __name__ == "__main__":
    main()
