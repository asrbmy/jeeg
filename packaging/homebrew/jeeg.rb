# Homebrew formula template for JeeG. Fill VERSION and SHA256 after the release is on PyPI:
#   curl -sL https://pypi.org/pypi/jeeg/VERSION/json | python3 -c "import json,sys;print([u for u in json.load(sys.stdin)['urls'] if u['packagetype']=='sdist'][0]['digests']['sha256'])"
# Then put this file in a tap repository (github.com/asrbmy/homebrew-jeeg/Formula/jeeg.rb):  brew install asrbmy/jeeg/jeeg
class Jeeg < Formula
  include Language::Python::Virtualenv

  desc "Type a task in plain words and it runs. No AI model, no account, no cloud"
  homepage "https://github.com/asrbmy/jeeg"
  url "https://files.pythonhosted.org/packages/source/j/jeeg/jeeg-VERSION.tar.gz"
  sha256 "SHA256"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/jeeg --version")
  end
end
