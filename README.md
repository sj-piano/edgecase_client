# edgecase_client

edgecase_client is a command-line tool for communicating with an Edgecase blockchain node.

It allows a user to:  
- Upload a draft article.  
- List draft articles.  
- Delete a draft article.  
- Sign an article.  



### Requirements

- Python 3.x (developed with 3.5.2).

- Python 2.x (developed with 2.7.12).

- Pytest 6.x (developed with 6.1.2).

- GPG 1.x, preferably 1.4.x (developed with 1.4.20).  
-- Required for creating or verifying signatures.

- Pip packages:  
-- colorlog (developed with 4.6.2). Required for colorised log output.

- The `shasum` tool. To produce SHA256 hashes, this tool uses the shell command `shasum -a 256 <filepath>`.



### Notes


Python 2 is only used to run an additional SHA256 implementation, as a double-check for asset SHA256 hashes.



### Installation

```
git clone --recurse-submodules git@github.com:sj-piano/edgecase_client.git
```

Now `cd` into the main directory, where you can run the tool `cli.py`.

```
cd edgecase_client

python3 cli.py --help
```



### Setup

In the directory `edgecase_client`, create a `config.ini` file.

It must contain this information:
```
[user]
author_name = stjohn_piano
author_key_name = stjohn_piano_2
long_user_id = 461955124538038826196103742383947089
```

Change the values to match those of your user profile.

You need to have your Edgecase-registered keypair in a `keys` directory, ready to be used to upload or sign a draft article.

Example:
- `stjohn_piano_2_public_key.txt`  
- `stjohn_piano_2_private_key.txt`  

Note: Typically, you'll use a secondary key (e.g. `stjohn_piano_2`) to interact with an Edgecase node and sign articles. The author_name within the article match the name of the secondary key i.e. in the top of the article there will be a line like this:  
```
<author_name>stjohn_piano_2</author_name>
```



### Upload a draft article

```
python3 cli.py --task uploadDraft --publicKeyDir=../keys/public_keys --privateKeyDir=../keys/private_keys --articleFile drafts/smart_contract_deployment.txt
```

Notes:  
- All option argument values can be indicated using an equals sign or a space.  
- The default publicKeyDir is `../keys/public_keys`, so if you place your keys here, this argument can be omitted.  
- The default privateKeyDir is `../keys/private_keys`, so if you place your keys here, this argument can be omitted.  



### List draft articles

```
python3 cli.py --task listDrafts
```



### Delete a draft

```
python3 cli.py --task deleteDraft --name smart_contract_deployment
```



### Sign a draft

```
python3 cli.py --task signDraft --publicKeyDir=../keys/public_keys --privateKeyDir=../keys/private_keys --articleFile drafts/smart_contract_deployment.txt --outputDir='signed_articles'


Notes:  
- The default outputDir is `signed_articles`, so if you choose this output directory, this argument can be omitted.  








